import os
import re
from datetime import datetime

from celery import Celery
from flask import Flask
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

# Globally accessible names
redis = FlaskRedis()
db = SQLAlchemy()

# Set up class for configuration
class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    CONFIG_JSON = os.environ.get('CONFIG_JSON', '{}')
    APPLICATION_ROOT = os.environ.get('PROXY_PATH', '/').strip() or '/'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql://root:devpassword@127.0.0.1/tgrains') #'sqlite://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STRING_MAX_LENGTH_TEXTAREA=10000
    STRING_MAX_LENGTH_AUTHOR=200
    STRING_MAX_LENGTH_EMAIL=254
    HASH_SALT = os.environ.get('HASH_SALT', 'salt.9yA8Uf5j4%1hr65Y1f8h1YGT1hj')

    HOST = 'localhost' if FLASK_ENV == 'development' else 'redis'
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://{}:6379/0'.format(HOST))
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    HELP_STRING = "TGRAINS Server"
    with open('templates/docs.md', 'r') as file:
        HELP_STRING = file.read()


# SQLAlchemy comment class
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(Config.STRING_MAX_LENGTH_TEXTAREA))
    author = db.Column(db.String(Config.STRING_MAX_LENGTH_AUTHOR))
    hash = db.Column(db.String(64))
    email = db.Column(db.String(Config.STRING_MAX_LENGTH_EMAIL))
    reply_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Factory function for flask app
def create_app(config_class=Config):
    _app = Flask(__name__)
    _app.config.from_object(config_class)

    redis.init_app(_app)
    db.init_app(_app)
    setup_db(_app, db)

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


# Setup database
def setup_db(_app, _db):
    # Get SQL Database connection parameters
    # Capture groups for each part of connection string
    p = re.compile('^(?P<proto>[A-Za-z]+):\/\/(?P<user>.+):(?P<pass>.+)\@(?P<host>[A-Za-z0-9\.]+):?(?P<port>\d+)?\/(?P<db>[A-Za-z0-9]+)?(\?(?P<params>.+))?$')
    m = p.match(_app.config['SQLALCHEMY_DATABASE_URI'])

    # Connect to the database and create the tgrains database if it doesn't exist
    # We need to do this because SQLAlchemy won't do it for us.
    engine = create_engine('{0}://{1}:{2}@{3}:{4}/?{5}'.format(m['proto'], m['user'], m['pass'], m['host'], m['port'] or '3306', m['params'] or 'charset=utf8mb4'))
    engine.execute('CREATE DATABASE IF NOT EXISTS {0};'.format(m['db'] if 'db' in m.groupdict() else 'tgrains'))
    engine.dispose()

    with _app.app_context():
        _db.create_all()