#!/usr/bin/env python3
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, render_template, redirect, url_for
import requests
import json
import db.service as DBService

app = Flask(__name__)


@app.route('/')
def home():
    sqlQuery = "SELECT * FROM node_addresses"
    res = DBService.query("node_addresses", sqlQuery)
    print(res)
    return render_template('index.html', table=res)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_node', methods = ['POST', 'GET'])
def register_node():
    if request.method == 'POST':
        payload = {
            "nodename": request.form['nodename'],
            "ip": request.form['ipaddr']
        }
        res = requests.post('http://0.0.0.0:4200/register/me', data=json.dumps(payload))
        if res.status_code == 201:
            return redirect(url_for('home'))
        else:
            return render_template("result.html", msg ="Error in adding new record")
            

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True,  port=4201)
