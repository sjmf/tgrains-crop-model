import re
import logging
from datetime import datetime

from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()
log = logging.getLogger(__name__)
strh = logging.StreamHandler()
strh.setLevel(logging.DEBUG)
strh.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s] %(message)s'))
log.addHandler(strh)
log.setLevel(logging.DEBUG)


def _as_dict_impl(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# SQLAlchemy comment class
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(Config.STRING_MAX_LENGTH_TEXTAREA), nullable=False)
    author = db.Column(db.String(Config.STRING_MAX_LENGTH_AUTHOR), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(Config.STRING_MAX_LENGTH_EMAIL), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True, nullable=False)

    tags = db.relationship("CommentTags", backref="comments")

    # JSON in MariaDB is just a LONGTEXT alias (holds 2^32 chars or 4GB data)
    # TEXT column holds 65,535 (2^16 - 1) characters or 64kb of data. Better for DoS attack protection!
    state = db.Column(db.Text)

    as_dict = _as_dict_impl


# SQLAlchemy Tags class
class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.Integer, nullable=False)

    as_dict = _as_dict_impl


# SQLAlchemy CommentTags class
class CommentTags(db.Model):
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), primary_key=True)
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
        for t in TAGS:
            tag = Tags(id=t[0], name=t[1], group=t[2])
            _db.session.add(tag)

        _db.session.commit()


TAGS = [
    (1,  'Business-as-usual', -1),
    (2,  'Small Business', 0),
    (3,  'Food Poverty', 0),
    (4,  'Consumption', 0),
    (5,  'Social Media', 0),
    (6,  'Education', 0),
    (7,  'Regulation', 0),
    (8,  'Government', 0),
    (9,  'Capitalism', 0),
    (10, 'Profits', 0),
    (11, 'Middle-actors', 0),
    (12, 'Wholesalers', 0),
    (13, 'Climate Change', 0),
    (14, 'Waste', 0),
    (15, 'Packaging', 0),
    (16, 'Expertise', 0),
    (17, 'Experience', 0),
    (18, 'Organic', 0),
    (19, 'No-Till', 0),

    (20, 'Soft fruit', 1),
    (21, 'Peas & Beans', 1),
    (22, 'Oats', 1),
    (23, 'Sugar Beet', 1),
    (24, 'Barley', 1),
    (25, 'Maize', 1),
    (26, 'Wheat', 1),
    (27, 'Vegetables', 1),
    (28, 'Oilseed Rape', 1),
    (29, 'Potatoes', 1),
    (30, 'Top fruit', 1),

    (31, 'Dairy Cattle', 1),
    (32, 'Beef Cattle', 1),
    (33, 'Chicken', 1),
    (34, 'Pork', 1),
    (35, 'Egg Production', 1),
    (36, 'Lowland Lamb', 1),
    (37, 'Upland Lamb', 1),

    (38, 'Production', 2),
    (39, 'Greenhouse Gas Emissions', 2),
    (40, 'Nitrogen Leaching', 2),
    (41, 'Profit', 2),
    (42, 'Calorie Production', 2),

    (43, 'Pesticide Impacts', 3),
    (44, 'Ground Water', 3),
    (45, 'Fish', 3),
    (46, 'Birds', 3),
    (47, 'Bees', 3),
    (48, 'Beneficial Arthropods', 3),

    (49, 'Nutrition', 4),
    (50, 'Vegetables', 4),
    (51, 'Tubers', 4),
    (52, 'Whole Grains', 4),
    (53, 'Plant Protein', 4),
    (54, 'Animal Protein', 4),
    (55, 'Added Sugars', 4),
    (56, 'Added Fats', 4),
    (57, 'Dairy', 4),
    (58, 'Fruit', 4),

    (59, 'Health', 5),
    (60, 'Stroke', 5),
    (61, 'Cancer', 5),
    (62, 'Heart Disease', 5),
    (63, 'Diabetes', 5),
]
