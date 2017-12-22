#!/usr/bin/env python3
from src import serverApp, socketio

socketio.run(serverApp, host='0.0.0.0', port=5200, debug=True)
