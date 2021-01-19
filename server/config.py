import os

from celery import Celery
from flask import Flask
from flask_redis import FlaskRedis

# Globally accessible names
redis = FlaskRedis()


# Set up class for configuration
class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    CONFIG_JSON = os.environ.get('CONFIG_JSON', '{}')
    APPLICATION_ROOT = os.environ.get('PROXY_PATH', '/').strip() or '/'
    # NB: Don't use 'localhost' here because MySQL connector assumes you want to look for a socket at /tmp/mysql.sock
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql://root:devpassword@127.0.0.1:3306/tgrains')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STRING_MAX_LENGTH_TEXTAREA = 10000
    STRING_MAX_LENGTH_AUTHOR = 200
    STRING_MAX_LENGTH_EMAIL = 254
    STRING_LENGTH_UNIQUE_ID = 34
    HASH_SALT = os.environ.get('HASH_SALT', 'salt.9yA8Uf5j4%1hr65Y1f8h1YGT1hj')

    HOST = '127.0.0.1' if FLASK_ENV == 'development' else 'redis'
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://{}:6379/0'.format(HOST))
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    BAU_PRECALC_RUNS = os.environ.get('BAU_PRECALC_RUNS', 2)

    with open('templates/docs.md', 'r') as file:
        HELP_STRING = file.read()


# Factory function for flask app
def create_app(config_class=Config):
    _app = Flask(__name__)
    _app.config.from_object(config_class)

    redis.init_app(_app)

    # Fix path when running behind a proxy (e.g. nginx, traefik, etc)
    if _app.config['FLASK_ENV'] == 'production':
        from werkzeug.middleware.proxy_fix import ProxyFix
        _app.wsgi_app = ProxyFix(_app.wsgi_app, x_for=1, x_host=1, x_proto=1, x_port=1)

    # Add CORS headers if an issue in development, for example if you run Flask on a different port to your UI
    @_app.after_request
    def after_request(response):
        if _app.config['FLASK_ENV'] == 'development':
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    return _app


# Setup Celery
def make_celery(_app):
    _celery = Celery(_app.import_name,
                     backend=_app.config['CELERY_RESULT_BACKEND'],
                     broker=_app.config['CELERY_BROKER_URL'])
    _celery.conf.update(_app.config)

    class ContextTask(_celery.Task):
        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return self.run(*args, **kwargs)

    # noinspection PyPropertyAccess
    _celery.Task = ContextTask
    return _celery
