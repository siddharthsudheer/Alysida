import json
from urllib.parse import urlparse
import socket
import requests
import falcon
import db.service as DBService

NOTIFICATION_URL = 'http://localhost:5200/notification'

# NOTIFICATION_URL = ''

def broadcast(payload, endpoint, request, isFile=False):
    """
        TODO: 
            • Make Async
            • Handle when peer doesn't respond 
              (and show error message accordingly - 404 maybe)
            • Separate 'POST' and 'GET'
              (broadcast should be only for Posting stuff to everyone)
    """
    my_ip=str(socket.gethostbyname(socket.gethostname()))
    sql_query = "SELECT IP FROM peer_addresses WHERE IP!='{}' AND REGISTRATION_STATUS='registered'".format(my_ip)
    query_result = DBService.query("peer_addresses", sql_query)
    if not query_result: # if 0 results for registered peers addrs returned
        response = 'No registered peers found. Please add peers and/or register with them.'
        return response
    else:
        ips = query_result['rows']
        peer_nodes = list(map(lambda i: 'http://{}:4200/'.format(i), ips))
        responses = list()

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
                peer_name = urlparse(peer).hostname
                if isFile:
                    resp = requests.get(url, stream=True)
                    responses.append({ 
                        'Peer': '{}'.format(peer_name),
                        'Response': resp 
                    })
                else:
                    resp = requests.get(url)
                    responses.append({ 
                        'Peer': '{}'.format(peer_name),
                        'Response': resp.json()
                    })

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


def notifier(event_name, data):
    payload = {
        "event_name": event_name,
        "data": data
    }
    if NOTIFICATION_URL:        
        ui_post = requests.post(NOTIFICATION_URL, data=json.dumps(payload))
        print(json.dumps(payload, indent=4))
    else:
        print(json.dumps(payload, indent=4))


def resolve_blockchain(blockchain):
    replaced = blockchain.resolve_conflicts()

    if replaced:
        #  check if selected txns are still in unconfirmed pool or not.
        final_title, final_msg = "Success", "Our chain was replaced"
        notifier("blockchain_replaced", None)
    else:
        # if selected txns are not in unconfirmed pool,
        # tell them to re-select if not replaced.. continue
        final_title, final_msg = "Success", "Our chain is authoritative"
        notifier("our_blockchain_authoritative", None)

    return (blockchain, final_title, final_msg)