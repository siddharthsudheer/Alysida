#!/usr/bin/env python3
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/notification', methods=['POST'])
def notification():
    if request.method == 'POST':
        data = json.loads(request.data, encoding='utf-8')
        socketio.emit('my_response', {'data': data['msg']}, namespace='/test')
    return


@socketio.on('my_event', namespace='/test')
def test_message(message):
    emit('my_response', {'data': message['data']})

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5201, debug=True)