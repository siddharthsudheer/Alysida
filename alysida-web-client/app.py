#!/usr/bin/env python3
import os
import sys

from flask import Flask, request, render_template, redirect, url_for,jsonify, make_response
import requests
import json

app = Flask(__name__)

ALYSIDA="http://localhost:4200"
getURL= lambda x: ALYSIDA + x

class ResponseParser():
    def __init__(self, res):
        self.received = res
        self.response = make_response(self._response_data(), self.received.status_code)
        self.response.headers = self._headers()

    def _headers(self):
        header_list = ['Content-Type', 'Server', 'Date']
        final_headers = dict()
        for h in header_list:
            final_headers[h] = self.received.headers[h]
        return final_headers

    def _response_data(self):
        x = json.loads(self.received.text)
        return jsonify(x)
    
    def parse(self):
        return self.response

@app.route('/add-peer-addresses')
def add_peer_addresses():
    url = getURL("/add-peer-addresses")
    payload = {
        "ips": ["10.0.0.101", "10.0.0.102", "10.0.0.103"]
        }
    res = requests.post(url, data=json.dumps(payload))
    response = ResponseParser(res).parse()
    return response


@app.route('/register-me')
def register_me():
    url = getURL("/register-me")
    res = requests.get(url)
    response = ResponseParser(res).parse()
    return response


@app.route('/get-peer-addresses')
def get_peer_addresses():
    url = getURL("/get-peer-addresses")
    res = requests.get(url)
    response = ResponseParser(res).parse()
    return response








if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True,  port=5200)
