#!/usr/bin/env python3
import logging, os, json
import markdown
from flask import Flask, Response, Blueprint, Markup, escape, request, redirect, url_for, abort

from CropModel import CropModel

HELPSTRING="""

# Crop Model API Routes

### /
_Methods:_ `GET`   

Return a help string

### /model
_Methods:_ `POST`

Post variables to the model for response. Takes a JSON object.

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

DEBUG = True
app.config.from_object(__name__)

flask_options = {
    'host': '0.0.0.0',
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
    return "test!"

@crops.route('model', methods=['POST'])
def model():
    v = request.get_json()
    model = CropModel()
    model.initialise_model()
    model.run_model()

    log.info(request)

    return Response(str(model), mimetype='application/json'), 200


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

