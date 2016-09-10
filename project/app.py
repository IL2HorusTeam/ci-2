# coding: utf-8

from verboselib import set_default_language
set_default_language('en')


from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('settings.py')


from flask.ext.cors import CORS
cors = CORS(app)


from .api.ws import Sockets
sockets = Sockets(app)


from .api import register_rest_blueprints, register_ws_blueprints
register_rest_blueprints(app)
register_ws_blueprints(sockets)
