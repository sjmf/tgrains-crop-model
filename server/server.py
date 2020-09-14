#!/usr/bin/env python3
import logging
import pickle
import markdown

from flask import Blueprint, Response, Markup, redirect, request, render_template, jsonify, url_for, escape
from redis.exceptions import ConnectionError

from config import redis, db, Comment, create_app, make_celery

# Set up logger
log = logging.getLogger(__name__)
app = create_app()
celery = make_celery(app)


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
    return Response(Markup("<!DOCTYPE html>\n<title>CropModel</title>\n") \
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

    # Pagination (load in pages)
    # Choose entities from model to load: exclude email, it should NEVER be returned to users
    query = Comment.query \
        .with_entities(Comment.id, Comment.author, Comment.reply_id, Comment.text, Comment.timestamp) \
        .order_by(Comment.id.desc())
    comments = query.paginate(page, size, True)
    length = query.count()

    return jsonify({
        'comments': [dict(zip([k['name'] for k in query.column_descriptions], [v for v in i])) for i in comments.items],
        'length': length,
        'page': page,
        'size': size
    })


@crops.route('comment', methods=['POST'])
def post_comment():
    data = request.get_json(force=True)
    log.info(data)

    # ALWAYS escape text taken from user to prevent XSS scriptjacking attacks
    reply_id = None if 'reply_id' not in data else int(data['reply_id'])

    # Sanity check input. None of the values are allowed to be empty strings
    if not data['text'] or data['text'].isspace() or \
        not data['author'] or data['author'].isspace() or \
        not data['email'] or data['email'].isspace():

        return "Bad request: empty comment fields are not allowed", 400

    # Add the comment to the database
    db.session.add(Comment(
        text=escape(data['text']),
        author=escape(data['author']),
        email=data['email'],  # I don't think we want to escape this, as it should NEVER be returned in the API
        reply_id=reply_id))
    db.session.commit()

    return redirect(url_for('crops.get_comments'), code=303)


# Register blueprint to the app
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
        #'threaded': True
    })
