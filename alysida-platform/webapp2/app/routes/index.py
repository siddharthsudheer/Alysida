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
        data = json.loads(request.data, encoding='utf-8')
        event_name = data['event_name']
        socketio.emit(event_name, {'data': data['data']}, namespace='/test')
    return

@socketio.on('get_event', namespace='/test')
def get_event(message):
    endpoint = endpoint_url(message['endpoint'])
    resp = requests.get(endpoint)
    if resp.status_code == 200:
        emit('get_event_resp', {'data': message['data']})


@socketio.on('my_event', namespace='/test')
def test_message(message):
    emit('my_response', {'data': message['data']})

@socketio.on('add-customer', namespace='/test')
def add_customer(customer):
    print(customer)
    emit('notification', {'message': 'new customer', 'customer': customer})


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
