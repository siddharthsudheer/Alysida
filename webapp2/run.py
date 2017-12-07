#!/usr/bin/env python3
from app import app, socketio

socketio.run(app, host='0.0.0.0', port=5201, debug=True)
