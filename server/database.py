import re, logging
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


# class TGRAINSModel(db.Model):
#     id                     = db.Column(db.Integer, primary_key=True)
#     cropAreas              = db.Column()
#     greenhouseGasEmissions = db.Column()
#     healthRiskFactors      = db.Column()
#     livestockAreas         = db.Column()
#     maxCropArea            = db.Column()
#     myUniqueLandscapeID    = db.Column()
#     nLeach                 = db.Column()
#     nutritionaldelivery    = db.Column()
#     pesticideImpacts       = db.Column()
#     production             = db.Column()
#     profit                 = db.Column()


# Setup database
def setup_db(_app, _db):
    # Initialize application for use with this database setup
    _db.init_app(_app)

    # Get SQL Database connection parameters
    # Capture groups for each part of connection string
    p = re.compile('^(?P<proto>[A-Za-z]+)://(?P<user>.+):(?P<pass>.+)@(?P<host>[A-Za-z0-9.]+):?(?P<port>\d+)?/(?P<db>[A-Za-z0-9]+)?(\?(?P<params>.+))?$')
    m = p.match(_app.config['SQLALCHEMY_DATABASE_URI'])

    # Connect to the database and create the tgrains database if it doesn't exist
    # We need to do this because SQLAlchemy won't do it for us.
    engine = create_engine('{0}://{1}:{2}@{3}:{4}/?{5}'.format(m['proto'], m['user'], m['pass'], m['host'], m['port'] or '3306', m['params'] or 'charset=utf8mb4'))
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
    (1,  'Small Business', 0),
    (2,  'Food Poverty', 0),
    (3,  'Consumption', 0),
    (4,  'Social Media', 0),
    (5,  'Education', 0),
    (6,  'Regulation', 0),
    (7,  'Government', 0),
    (8,  'Capitalism', 0),
    (9,  'Profits', 0),
    (10, 'Middle-actors', 0),
    (11, 'Wholesalers', 0),
    (12, 'Climate Change', 0),
    (13, 'Waste', 0),
    (14, 'Packaging', 0),
    (15, 'Expertise', 0),
    (16, 'Experience', 0),
    (17, 'Organic', 0),
    (18, 'No-Till', 0),

    (19, 'Soft fruit', 1),
    (20, 'Peas & Beans', 1),
    (21, 'Oats', 1),
    (22, 'Sugar Beet', 1),
    (23, 'Barley', 1),
    (24, 'Maize', 1),
    (25, 'Wheat', 1),
    (26, 'Vegetables', 1),
    (27, 'Oilseed Rape', 1),
    (28, 'Potatoes', 1),
    (29, 'Top fruit', 1),

    (30, 'Dairy Cattle', 1),
    (31, 'Beef Cattle', 1),
    (32, 'Chicken', 1),
    (33, 'Pork', 1),
    (34, 'Egg Production', 1),
    (35, 'Lowland Lamb', 1),
    (36, 'Upland Lamb', 1),

    (37, 'Production', 2),
    (38, 'Greenhouse Gas Emissions', 2),
    (39, 'Nitrogen Leaching', 2),
    (40, 'Profit', 2),
    (41, 'Calorie Production', 2),

    (42, 'Pesticide Impacts', 3),
    (43, 'Ground Water', 3),
    (44, 'Fish', 3),
    (45, 'Birds', 3),
    (46, 'Bees', 3),
    (47, 'Beneficial Arthropods', 3),

    (48, 'Nutrition', 4),
    (49, 'Vegetables', 4),
    (50, 'Tubers', 4),
    (51, 'Whole Grains', 4),
    (52, 'Plant Protein', 4),
    (53, 'Animal Protein', 4),
    (54, 'Added Sugars', 4),
    (55, 'Added Fats', 4),
    (56, 'Dairy', 4),
    (57, 'Fruit', 4),

    (58, 'Health', 5),
    (59, 'Stroke', 5),
    (60, 'Cancer', 5),
    (61, 'Heart Disease', 5),
    (62, 'Diabetes', 5)
]