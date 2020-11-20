#!/usr/bin/env python3
import logging
import pickle
import markdown
import hashlib
import json

from flask import Blueprint, Response, Markup, redirect, request, render_template, jsonify, url_for, escape
from redis.exceptions import ConnectionError
from sqlalchemy import and_

from config import redis, create_app, make_celery
from database import setup_db, db, Comments, Tags, CommentTags, State, User

# Set up logger
log = logging.getLogger(__name__)
app = create_app()
celery = make_celery(app)

db.init_app(app)
setup_db(app, db)

'''
Application Routes
'''
# Look at end of file for where this blueprint is actually registered to the app
crops = Blueprint('crops', __name__, template_folder='templates')

# Development / debug routes. Not available in production
if app.config['FLASK_ENV'] == 'development':
    @crops.route('/echo', methods=['GET', 'POST'])
    def echo():
        log.info(request.headers)
        return Response("{}\n{}".format(str(request.headers), request.get_data().decode('utf-8')),
                        mimetype='text/plain'), 200


    @crops.route('/test', methods=['GET'])
    def test():
        log.info(request)
        return render_template('test.html')


@crops.route('/', methods=['GET'])
def index():
    log.info(request)
    return Response(Markup("<!DOCTYPE html>\n<title>CropModel</title>\n")
                    + Markup(markdown.markdown(app.config['HELP_STRING']))), 200


@crops.route('model', methods=['POST'])
def model_post():
    # data = request.form.to_dict(flat=True)
    data = request.get_json()
    log.info(data)

    task = celery.send_task('celery_model_run', kwargs={'data': data, 'landscape_id': data['landscape_id']},
                            expires=120)

    return jsonify({'task_id': task.id}), 303, {'Location': url_for('crops.task_status', task_id=task.id)}


@crops.route('model', methods=['GET'])
def model_get():
    return cached_task('celery_model_get_bau', request.args.get('landscape_id'))


@crops.route('strings', methods=['GET'])
def strings_get():
    return cached_task('celery_get_strings', request.args.get('landscape_id'))


# Helper function: cache a celery task
def cached_task(task_name, landscape_id):
    if landscape_id is None:
        return 'Bad Request: Must provide landscape_id=101 or 102 as parameter!', 400

    redis_key = "flask:{0}:{1}".format(task_name, landscape_id)

    # Need only ever run celery task once per landscape ID: check for a stored key in Redis
    exists = redis.get(redis_key)
    if exists:
        try:
            task = pickle.loads(exists)
            log.info("Cache HIT: {} / {} / {}".format(redis_key, task.id, task.state))

            # Don't return the cache if it failed!
            if task.state != "FAILURE":
                return see_other_redirect(task)

        except ConnectionError as e:
            log.error(e)
            log.error("redis.exceptions.ConnectionError is likely due to stale Celery tasks in Redis.")
            log.error("Clear the redis cache (e.g. using redis_client.flushall()) and try again.")

    # If not exists, run celery task:
    task = celery.send_task(task_name, kwargs={'landscape_id': landscape_id}, expires=120)

    # Cache the landscape ID against the task in Redis on first-run under key strings_get:101|102
    # Expires in 24h, same as the celery task - this means we won't need to check if the
    # task still exists because it'll expire automatically.
    redis.setex(redis_key, 86400, value=pickle.dumps(task))

    # Return existing celery task which can be queried with /status
    return see_other_redirect(task)


# Helper function - redirect with HTTP 303 SEE OTHER
def see_other_redirect(task):
    return jsonify({'task_id': task.id}), 303, {'Location': url_for('crops.task_status', task_id=task.id)}


@crops.route('/status/<task_id>')
def task_status(task_id):
    task = celery.AsyncResult(task_id)

    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@crops.route('comment', methods=['GET'])
def get_comments():
    data = request.args.to_dict(flat=True)
    log.info(data)

    try:
        page = int(request.args.get('page'))
        size = int(request.args.get('size'))
    except (ValueError, TypeError) as e:
        log.error(e)
        page, size = (1, 5)

    # Query model
    query = Comments.query.order_by(Comments.id.desc())

    # Pagination (load in pages)
    comments = query.paginate(page, size, True).items
    items = [i.as_dict() for i in comments]

    for i, c in enumerate(items):
        c['timestamp'] = c['timestamp'].timestamp()
        c['tags'] = [t.tag_id for t in list(comments[i].tags)]

        if c['reply_id']:
            c['reply'] = get_single_comment(c['reply_id'])

        c['state'] = json.loads(comments[i].state.state)
        c['author'] = comments[i].author.name

    return jsonify({
        'comments': items,
        'length': query.count(),
        'page': page,
        'size': size
    })


@crops.route('reply', methods=['GET'])
def load_comment_by_id():
    return jsonify(get_single_comment(request.args.get('id')))


def get_single_comment(reply_id):
    query = Comments.query.filter_by(id=reply_id)
    comment = query.first().as_dict()
    comment['timestamp'] = comment['timestamp'].timestamp()
    comment['tags'] = [t.tag_id for t in list(query.first().tags)]
    del comment['email']

    return comment


@crops.route('comment', methods=['POST'])
def post_comment():
    data = request.get_json(force=True)

    # ALWAYS escape text taken from user to prevent XSS scriptjacking attacks
    reply_id = None if 'reply_id' not in data else int(data['reply_id'])

    try:
        # Sanity check input. None of the values are allowed to be empty strings
        if (not data['text'] or data['text'].isspace()) or \
                (not data['user_id'] or data['user_id'].isspace()) or \
                (not data['author'] or data['author'].isspace()) or \
                (not data['email'] or data['email'].isspace()):

            log.error("Bad request: comment is missing metadata")
            return "Bad request: comment is missing metadata", 400

    except KeyError as e:
        log.error("Bad request: comment is missing metadata")
        return "Bad request: comment is missing metadata", 400

    log.info(data)

    # Update user object with the author's name and email
    add_and_update_user(uid=data['user_id'], name=data['author'], email=data['email'])

    # Add the comment to the database
    comment = Comments(
        text=escape(data['text']),
        user_id=data['user_id'],
        hash=hashlib.sha256((data['email'] + app.config['HASH_SALT']).encode('utf-8')).hexdigest(),
        state_session_id=data['session_id'],
        state_index=data['index'],
        reply_id=reply_id
    )

    # Retrieve tags from request and store as rows in CommentTags table
    db.session.add(comment)
    db.session.flush()      # Generate PKs

    for tag_id in data['tags']:
        db.session.add(CommentTags(comment_id=comment.id, tag_id=tag_id))

    db.session.commit()

    return redirect(url_for('crops.get_comments', page=data['page'], size=data['size']), code=303)


@crops.route('tags', methods=['GET'])
def get_tags():
    query = Tags.query.order_by(Tags.id)
    groups = [i[0] for i in query.group_by(Tags.group).with_entities(Tags.group)]

    return jsonify({
        'tags': {
            i.as_dict()['id']: {k: i.as_dict()[k] for k in i.as_dict() if k != "id"}
            for i in query
        },
        'groups': {
            g: [i['id'] for i in list(filter(lambda x: x['group'] == g, [i.as_dict() for i in query]))]
            for g in groups
        }
    })


@crops.route('state', methods=['POST'])
def post_state():
    data = request.get_json(force=True)

    # Sanity check input. None of the values are allowed to be empty strings
    if (not data['session_id'] or data['session_id'].isspace()) or \
        (not data['user_id'] or data['user_id'].isspace()) or \
            'index' not in data.keys():

        log.error("Bad request: missing data")
        return "Bad request: missing data", 400

    log.info("{} - index {}".format(data['session_id'], data['index']))

    add_and_update_user(uid=data['user_id'])

    if 'state' in data.keys():
        State.create(
            session_id=data['session_id'],
            index=data['index'],
            user_id=data['user_id'],
            state=json.dumps(data['state'])
        )

    elif 'deleted' in data.keys():
        state = db.session.query(State).filter(and_(
            State.session_id == data['session_id'],
            State.index == data['index'],
            State.user_id == data['user_id']
        )).update({
            'deleted': data['deleted']
        })

        db.session.commit()

    return Response("OK", mimetype='text/plain'), 200


def add_and_update_user(uid, name=None, email=None):
    user = User.query.get(uid)
    log.info("USER ID {} RESULT {}".format(uid, user))

    if user is None:
        User.create(
            id=uid,
            name=escape(name) if name else None,
            email=email     # Don't escape email, as it should NEVER be returned in the API or displayed
        )

    elif name is not None and email is not None:
        user.name = name
        user.email = email
        db.session.commit()

    return


#
# Register blueprint to the app
#
app.register_blueprint(crops, url_prefix=app.config['APPLICATION_ROOT'])


'''
    Gunicorn logging options. Not run in dev server
'''
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

'''
    Main. Does not run when running with WSGI
'''
if __name__ == "__main__":
    strh = logging.StreamHandler()
    strh.setLevel(logging.DEBUG)
    strh.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s] %(message)s'))
    log.addHandler(strh)
    log.setLevel(logging.DEBUG)

    log.debug(app.url_map)
    app.run(**{
        'host': '0.0.0.0',
        'debug': True,
        # 'port': 8000
        # 'threaded': True
    })
