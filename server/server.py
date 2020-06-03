#!/usr/bin/env python3
import logging, os, json
import markdown
from flask import Flask, Response, Blueprint, Markup, request, render_template

from model.CropModel import CropModel


HELPSTRING="""
# Crop Model API Routes

### [/ (index)](/)
_Method:_ `GET`   
Return this help string


### [/test](/test)
_Method:_ `GET`

Returns a HTML test form which can be used to POST values to the `/model` endpoint.


### [/model](/model)
_Method:_ `GET`

Get the BAU (Business as usual) state. Takes a variable for landscape ID, e.g.:

`GET /model?landscape_id=101`

Valid landscape IDs are currently 101, 102.


### [/model](/model)
_Method:_ `POST`

Post variables to the model for response. POST body MUST include all the below variables. Values (with the exception of
`landscape_id`, an integer) are in hectares and will be interpreted as float-point numbers.

* landscape_id = 101
* wheat        = 400
* barley       = 400
* oats         = 200
* oilseed      = 800
* vegetables   = 800
* livestock    = 400
* maize        = 400
* beans        = 200
* potatoes     = 800
* onion        = 800
* cow          = 300
* sheep        = 200
* pig          = 100

"""

# Set up logger
log = logging.getLogger(__name__)

# Create flask app
app = Flask(__name__)

# Set up blueprint
APPLICATION_ROOT = os.environ.get('PROXY_PATH', '/').strip() or '/'
#from werkzeug.middleware.proxy_fix import ProxyFix
#app.wsgi_app = ProxyFix(app.wsgi_app)

crops = Blueprint('crops', __name__, template_folder='templates')
# Look at end of file for where this blueprint is actually registered to the app

# Configuration
CONFIG_JSON = os.environ.get('CONFIG_JSON', '{}')
FLASK_ENV='development'

app.config.from_object(__name__)

flask_options = {
    'host': '0.0.0.0',
    'debug': True,
    #'threaded': True
}


# Testing
#@app.after_request
#def after_request(response):
#    response.headers.add('Access-Control-Allow-Origin', '*')
#    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#    return response

'''
    Application Routes
'''
@crops.route('/', methods=['GET'])
def index():
    log.info(request)
    return Response(Markup("<!DOCTYPE html>\n<title>CropModel</title>\n") \
            + Markup(markdown.markdown(HELPSTRING))) , 200


@crops.route('/test', methods=['GET'])
def test():
    log.info(request)
    return render_template('test.html')


@crops.route('model', methods=['GET'])
def model_get():
    landscape_id = request.args.get('landscape_id')

    # Initialise crop model
    model = CropModel()
    if landscape_id:
        model.set_landscape_id(int(landscape_id))
    model.initialise_model()
    model.run_model()
    log.info(request)

    return Response(json.dumps(model.toDict()), mimetype='application/json'), 200
    #return Response(str(model), mimetype='application/json'), 200


@crops.route('model', methods=['POST'])
def model_post():
    data = request.form
    log.info(data)

    # Initialise crop model
    model = CropModel()
    model.set_landscape_id(int(data['landscape_id']))
    model.initialise_model()

    max_crops = len(model.cropAreasBAU)
    crop_areas = []
    for i in range(0, max_crops):
        crop = model.get_crop_string(i).lower().split(' ')[0]
        area = float(data[crop])
        #log.info("{}={}".format(crop, area))
        crop_areas.append(area)

    max_livestock = len(model.livestockNumbersBAU)
    livestock_areas = []
    for i in range(0, max_livestock):
        livestock = model.get_livestock_string(i).lower()#.split(' ')[0]
        area = int(data[livestock])                             #TODO: This will likely need to change to type float
        #log.info("{}={}".format(livestock, area))
        livestock_areas.append(area)

    # set crop areas takes an ordered list of float point numbers
    model.set_crop_areas(crop_areas)
    model.set_livestock_areas(livestock_areas)
    model.run_model()
    log.info(request)

    return Response(json.dumps(model.toDict()), mimetype='application/json'), 200
    #return Response(str(model), mimetype='application/json'), 200


# Register blueprint to the app
app.register_blueprint(crops, url_prefix=APPLICATION_ROOT)


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
    app.run(**flask_options)

