#!/usr/bin/env python3
import json
from app import app, socketio
from flask import Flask, render_template, request, url_for, send_from_directory
from flask_socketio import SocketIO, emit
import requests


endpoint_url = lambda x: 'http://localhost:4200/{}'.format(x)

@app.route('/')
@app.route('/transactions')
@app.route('/example-customer')
def root():
    return app.send_static_file('pages/mainPage/views/index.html')

@app.route('/notification', methods=['POST'])
def notification():
    if request.method == 'POST':
        print("HEREEEE")
        print(request.data)
        data = json.loads(request.data, encoding='utf-8')
        event_name = data['event_name']
        print(data)
        socketio.emit(event_name, {'data': data['data']}, namespace='/test')
    return 'okay'

@socketio.on('get_event', namespace='/test')
def get_event(message):
    print(message)
    endpoint = endpoint_url(message['endpoint'])
    resp = requests.get(endpoint)
    if resp.status_code == 200 or resp.status_code == 201:
        emit('get_event_resp', {'data': resp.json()})

@socketio.on('post_event', namespace='/test')
def post_event(payload):
    print(payload)
    endpoint = endpoint_url(payload['endpoint'])
    resp = requests.post(endpoint, data=json.dumps(payload['data']))
    print(resp)
    if resp.status_code == 201:
        emit('post_event_resp', {'data': 'success'})
    else:
        print("\nFAILED:\n{}\Response:\n{}".format(payload, resp))
        emit('post_event_resp', {'data': 'fail', 'resp': resp})

@socketio.on('get_peers', namespace='/test')
def get_peers(message):
    print(message)
    endpoint = endpoint_url(message['endpoint'])
    resp = requests.get(endpoint)
    if resp.status_code == 200 or resp.status_code == 201:
        emit('get_peers_resp', {'data': resp.json()})

@socketio.on('post_peers', namespace='/test')
def post_peers(payload):
    print(payload)
    endpoint = endpoint_url(payload['endpoint'])
    resp = requests.post(endpoint, data=json.dumps(payload['data']))
    print(resp)
    if resp.status_code == 201 or resp.status_code == 202:
        emit('post_peers_resp', {'data': 'success'})
    else:
        print("\nFAILED:\n{}\Response:\n{}".format(payload, resp))
        emit('post_peers_resp', {'data': 'fail', 'resp': resp})

@socketio.on('do_consensus', namespace='/test')
def do_consensus(message):
    print(message)
    endpoint = endpoint_url(message['endpoint'])
    resp = requests.get(endpoint)
    if resp.status_code == 200 or resp.status_code == 201:
        emit('do_consensus_resp', {'data': resp.json()})

@socketio.on('connect', namespace='/test')
def test_connect():
    print('connected')
    emit('my_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
