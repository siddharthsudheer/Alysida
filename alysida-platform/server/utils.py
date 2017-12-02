import os
import json
import re
from urllib.parse import urlparse
import socket
import requests
import falcon
import hashlib
import db.service as DBService

def broadcast(payload, endpoint, request):
    """
        TODO: 
            • Make Async
            • Handle when peer doesn't respond 
              (and show error message accordingly - 404 maybe)
            • Separate 'POST' and 'GET'
              (broadcast should be only for Posting stuff to everyone)
    """
    my_ip=str(socket.gethostbyname(socket.gethostname()))
    sql_query = "SELECT IP FROM peer_addresses WHERE IP!='{}' AND REGISTRATION_STATUS!='unregistered'".format(my_ip)
    query_result = DBService.query("peer_addresses", sql_query)
    if not query_result: # if 0 results for peers addrs returned
        response = 'No registered peers found. Please add peers and/or register with them.'
        return response
    else:
        ips = query_result['rows']
        peer_nodes = list(map(lambda i: 'http://{}:4200/'.format(i), ips))
        # peer_nodes = ['http://localhost:4201/']

        if request == 'POST':
            responses = list()

            for peer in peer_nodes:
                url = peer + endpoint
                resp = requests.post(url, data=json.dumps(payload))
                waw = resp.json()
                responses.append({ 
                    'Peer': '{}'.format(peer),
                    'Response': waw
                    })
            return responses

        elif request == 'GET':
            responses = []

            for peer in peer_nodes:
                url = peer + endpoint
                peer_name = urlparse(peer).netloc
                resp = (re.sub('[^A-Za-z0-9]+', '', peer_name), requests.get(url, stream=True))
                responses.append(resp)

            return responses


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