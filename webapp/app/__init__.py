#!/usr/bin/env python3
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__, static_url_path='')

app.url_map.strict_slashes = False

socketio = SocketIO(app)

from app.routes import index
