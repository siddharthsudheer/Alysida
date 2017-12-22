#!/usr/bin/env python3
from flask import Flask
from flask_socketio import SocketIO

serverApp = Flask(__name__, static_folder='app', static_url_path='')

# serverApp.url_map.strict_slashes = False

socketio = SocketIO(serverApp)

from src.server import index
