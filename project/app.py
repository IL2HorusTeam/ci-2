# -*- coding: utf-8 -*-

from flask import Flask
from flask_sockets import Sockets
from flask.ext.cors import CORS


app = Flask(__name__)
app.config.from_pyfile('settings.py')

cors = CORS(app)
sockets = Sockets(app)


from .services import *
