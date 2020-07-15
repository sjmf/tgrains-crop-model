#!/usr/bin/env python3
import logging, os
import markdown
from flask import Flask, Response, Blueprint, Markup, request, render_template, jsonify, url_for
from celery import Celery

HELPSTRING="""
# Crop Model API Routes

### [/ (index)](/)
_Method:_ `GET`   
Return this help string


### [/test](/test)
_Method:_ `GET`

**FLASK_ENV=development ONLY** 

Returns a HTML test form which can be used to POST values to the `/model` endpoint.


### [/echo](/echo)
_Method:_ `POST`

**FLASK_ENV=development ONLY** 

Echos whatever POST request it received back at the browser. 


### [/strings](/strings?landscape_id=101)
_Method:_ `GET`

Get the list of crop and livestock strings. Takes a variable for landscape ID, e.g.:

`GET /strings?landscape_id=101`


### [/model](/model?landscape_id=101)
_Method:_ `GET`

Get the BAU (Business as usual) state. Takes a variable for landscape ID, e.g.:

`GET /model?landscape_id=101`

Valid landscape IDs are currently 101, 102.


### [/model](/model)
_Method:_ `POST`

Post variables to the model for response. POST body MUST include all the below variables, formatted as JSON. Values 
(with the exception of `landscape_id`, an integer) are in hectares and will be interpreted as float-point numbers.

* landscape_id = 101
* (Crop and livestock variables, which are now retrieved via [/strings](strings?landscape_id=101))


"""

# Set up logger
log = logging.getLogger(__name__)

# Create flask app
app = Flask(__name__)

# Set up configuration
FLASK_ENV=os.environ.get('FLASK_ENV', 'development')
CONFIG_JSON = os.environ.get('CONFIG_JSON', '{}')
APPLICATION_ROOT = os.environ.get('PROXY_PATH', '/').strip() or '/'

# Fix path when running behind a proxy (e.g. nginx, traefik, etc)
if FLASK_ENV == 'production':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1, x_port=1)

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
host = 'localhost' if FLASK_ENV == 'development' else 'redis'
app.config['CELERY_BROKER_URL'] = 'redis://{}:6379/0'.format(host)
app.config['CELERY_RESULT_BACKEND'] = 'redis://{}:6379/0'.format(host)
celery = make_celery(app)


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
            + Markup(markdown.markdown(HELPSTRING))) , 200


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
    return celery_get(request.args.get('landscape_id'), 'celery_model_get_bau')


@crops.route('strings', methods=['GET'])
def strings_get():
    return celery_get(request.args.get('landscape_id'), 'celery_get_strings')


# Helper function - abstract 'get'-type task for the routes above
def celery_get(landscape_id, task_name):
    if landscape_id is None:
        return 'Bad Request: Must provide landscape_id=101 or 102 as parameter!', 400

    task = celery.send_task(task_name, kwargs={'landscape_id': landscape_id}, expires=120)
    log.info(task.id)
    return jsonify({'task_id': task.id}), 303, {'Location': url_for('task_status', task_id=task.id)}


@app.route('/status/<task_id>')
def task_status(task_id):

    task = celery.AsyncResult(task_id)
    log.info(task)
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

