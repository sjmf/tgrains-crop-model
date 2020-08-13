#!/usr/bin/env python3
import logging, os, pickle

import markdown
from flask import Flask, Response, Blueprint, Markup, request, render_template, jsonify, url_for
from flask_redis import FlaskRedis
from redis.exceptions import ConnectionError
from celery import Celery

HELP_STRING= "TGRAINS Server"
with open('templates/docs.md', 'r') as file:
    HELP_STRING = file.read()

# Set up logger
log = logging.getLogger(__name__)

# Create flask app
app = Flask(__name__)

# Set up configuration
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
CONFIG_JSON = os.environ.get('CONFIG_JSON', '{}')
APPLICATION_ROOT = os.environ.get('PROXY_PATH', '/').strip() or '/'

# Fix path when running behind a proxy (e.g. nginx, traefik, etc)
if FLASK_ENV == 'production':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1, x_port=1)

# Redis cache URL
HOST = 'localhost' if FLASK_ENV == 'development' else 'redis'
REDIS_URL = os.environ.get('REDIS_URL', 'redis://{}:6379/0'.format(HOST))

crops = Blueprint('crops', __name__, template_folder='templates')
# Look at end of file for where this blueprint is actually registered to the app

app.config.from_object(__name__)

# Setup Celery
def make_celery(_app):

    _celery = Celery(
        _app.import_name,
        backend=_app.config['CELERY_RESULT_BACKEND'],
        broker=_app.config['CELERY_BROKER_URL']
    )
    _celery.conf.update(_app.config)

    class ContextTask(_celery.Task):
        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return self.run(*args, **kwargs)

    # noinspection PyPropertyAccess
    _celery.Task = ContextTask
    return _celery

# Celery task queue details
# Need to place this in app.config as config.from_object(__name__) already called above
app.config['CELERY_BROKER_URL'] = REDIS_URL
app.config['CELERY_RESULT_BACKEND'] = REDIS_URL
celery = make_celery(app)

# Create redis cache
redis_client = FlaskRedis(app)

# Add CORS headers if an issue in development, for example if you run Flask on a different port to your UI
@app.after_request
def after_request(response):
    if FLASK_ENV == 'development':
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


'''
    Application Routes
'''
@crops.route('/', methods=['GET'])
def index():
    log.info(request)
    return Response(Markup("<!DOCTYPE html>\n<title>CropModel</title>\n") \
                    + Markup(markdown.markdown(HELP_STRING))) , 200


# Development / debug routes. Not available in production
if FLASK_ENV == 'development':
    @crops.route('/echo', methods=['GET', 'POST'])
    def echo():
        log.info(request.headers)
        return Response("{}\n{}".format(str(request.headers), request.get_data().decode('utf-8')), mimetype='text/plain'), 200


    @crops.route('/test', methods=['GET'])
    def test():
        log.info(request)
        return render_template('test.html')


@crops.route('model', methods=['POST'])
def model_post():
    #data = request.form.to_dict(flat=True)
    data = request.get_json()
    log.info(data)

    task = celery.send_task('celery_model_run', kwargs={'data': data, 'landscape_id': data['landscape_id']}, expires=120)

    return jsonify({'task_id': task.id}), 303, {'Location': url_for('task_status', task_id=task.id)}


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
    exists = redis_client.get(redis_key)
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
    redis_client.setex(redis_key, 86400, value=pickle.dumps(task))

    # Return existing celery task which can be queried with /status
    return see_other_redirect(task)


# Helper function - redirect with HTTP 303 SEE OTHER
def see_other_redirect(task):
    return jsonify({'task_id': task.id}), 303, {'Location': url_for('task_status', task_id=task.id)}


@app.route('/status/<task_id>')
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


# Register blueprint to the app
app.register_blueprint(crops, url_prefix=APPLICATION_ROOT)


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
        #'threaded': True
    })

