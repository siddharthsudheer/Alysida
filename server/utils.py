import os
import json
import re
from urllib.parse import urlparse
import socket
import requests
import falcon
import db.service as DBService


def broadcast(payload, endpoint, request):
    # Make Async
    sql_query = "SELECT IP FROM node_addresses"
    ips = DBService.query("node_addresses", sql_query)['rows']
    # my_ip = socket.gethostbyname(socket.gethostname())
    peer_nodes = list(map(lambda i: 'http://{}:4200/'.format(i), ips))
    # peer_nodes = ['http://localhost:4201/', 'http://localhost:4202/', 'http://localhost:4203/']

    if request == 'POST':
        for peer in peer_nodes:
            url = peer + endpoint
            requests.post(url, data=json.dumps(payload))
    elif request == 'GET':
        response = []
        for peer in peer_nodes:
            url = peer + endpoint
            peer_name = urlparse(peer).netloc
            resp = (re.sub('[^A-Za-z0-9]+', '', peer_name),
                    requests.get(url, stream=True))
            response.append(resp)
        return response


def parse_post_req(req):
    try:
        raw_json = req.stream.read()
    except Exception as ex:
        raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)
    try:
        result_json = json.loads(raw_json, encoding='utf-8')
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed JSON',
                               'Could not decode the request body. The '
                               'JSON was incorrect.')
    return result_json
