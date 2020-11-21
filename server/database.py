import re
import logging
from datetime import datetime

from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

db = SQLAlchemy()
log = logging.getLogger(__name__)
strh = logging.StreamHandler()
strh.setLevel(logging.DEBUG)
strh.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s] %(message)s'))
log.addHandler(strh)
log.setLevel(logging.DEBUG)


# Mixins for database class methods
class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Store history states from users in DB
class State(BaseMixin, db.Model):
    session_id = db.Column(db.String(Config.STRING_LENGTH_UNIQUE_ID), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.String(Config.STRING_LENGTH_UNIQUE_ID), db.ForeignKey('user.id'), nullable=False)

    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True, nullable=False)
    deleted = db.Column(db.Boolean, default=False)

    # JSON in MariaDB is just a LONGTEXT alias (holds 2^32 chars or 4GB data)
    # TEXT column holds 65,535 (2^16 - 1) characters or 64kb of data. Better for DoS attack protection!
    state = db.Column(db.Text)


# Store users in DB
class User(BaseMixin, db.Model):
    id = db.Column(db.String(Config.STRING_LENGTH_UNIQUE_ID), primary_key=True, nullable=False)
    name = db.Column(db.String(Config.STRING_MAX_LENGTH_AUTHOR))
    email = db.Column(db.String(Config.STRING_MAX_LENGTH_EMAIL))
    hash = db.Column(db.String(64))

    comments = db.relationship('Comments', backref="user", lazy=True)


# SQLAlchemy comment class
class Comments(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(Config.STRING_MAX_LENGTH_TEXTAREA), nullable=False)
    user_id = db.Column(db.String(Config.STRING_LENGTH_UNIQUE_ID), db.ForeignKey('user.id'), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True, nullable=False)
    distance = db.Column(db.Integer, nullable=False)

    # Reference into State table on composite key
    state_session_id = db.Column(db.String(Config.STRING_LENGTH_UNIQUE_ID), nullable=False)
    state_index = db.Column(db.Integer, nullable=False)

    # Back refs
    author = db.relationship("User", backref="comments_author")
    tags = db.relationship("CommentTags", backref="comments", cascade="all, delete",  passive_deletes=True)
    state = db.relationship("State", backref="comments_state", cascade="all, delete")

    # FK Relationship
    __table_args__ = db.ForeignKeyConstraint([state_session_id, state_index], [State.session_id, State.index]), {}


# SQLAlchemy Tags class
class Tags(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.Integer, nullable=False)


# SQLAlchemy CommentTags class
class CommentTags(BaseMixin, db.Model):
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete="CASCADE"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)


# ==================
# Methods

# Setup database
def setup_db(_app, _db):
    # Initialize application for use with this database setup
    _db.init_app(_app)

    # Get SQL Database connection parameters
    # Capture groups for each part of connection string
    p = re.compile(r'^(?P<proto>[A-Za-z]+)://(?P<user>.+):(?P<pass>.+)@'
                   r'(?P<host>[A-Za-z0-9.]+):?(?P<port>\d+)?/'
                   r'(?P<db>[A-Za-z0-9]+)?(\?(?P<params>.+))?$')
    m = p.match(_app.config['SQLALCHEMY_DATABASE_URI'])

    # Connect to the database and create the tgrains database if it doesn't exist
    # We need to do this because SQLAlchemy won't do it for us.
    engine = create_engine('{0}://{1}:{2}@{3}:{4}/?{5}'.format(
        m['proto'],
        m['user'],
        m['pass'],
        m['host'],
        m['port'] or '3306',
        m['params'] or 'charset=utf8mb4')
    )
    db_name = m['db'] if 'db' in m.groupdict() else 'tgrains'
    engine.execute('CREATE DATABASE IF NOT EXISTS {0};'.format(db_name))
    engine.execute('USE {0};'.format(db_name))

    with _app.app_context():
        _db.create_all()
        _insert_tags(_db, engine)

    engine.dispose()


def _insert_tags(_db, _engine):
    # Count tags in database
    count = _engine.execute('SELECT COUNT(*) FROM {0};'.format(Tags.__table__)).fetchall()[0][0]

    if count == 0:
        log.info('Populating tags table in database...')
        with open('sql/tgrains_tags.sql', 'r') as file:
            escaped_sql = text(file.read())
            _engine.execute(escaped_sql)

        _db.session.commit()

