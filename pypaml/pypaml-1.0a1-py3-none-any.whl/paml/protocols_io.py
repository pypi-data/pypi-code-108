import requests

client_id = 'pr_live_id_89dda9cd325612475178d54c6629209f'
client_secret = 'pr_live_sc_c39a1b25b7136c52e60c3901f7fe3506'
access_token = '7bafddb94a8aef42f8d7b7fb3ad11c7ac304bb11f259b35b6c82f18188afdeac'
private_access_token = '7bafddb94a8aef42f8d7b7fb3ad11c7ac304bb11f259b35b6c82f18188afdeac'

def get_protocol(protocol_id, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    protocol_endpoint = f'https://www.protocols.io/api/v3/protocols/{protocol_id}'
    response = requests.get(protocol_endpoint, headers=headers)

def create_protocol(guid, access_token):
    create_endpoint = f'https://www.protocols.io/api/v3/protocols/{guid}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    data = {
      'type_id': 4,
    }
    # type_id
    #optional, default is 1
    #int
    #protocol type id
    #1 - protocol
    #3 - collection
    #4 - document
    response = requests.post(create_endpoint, headers=headers, data=data)
    print(response.content)


def request_client(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    client_request_endpoint = f'https://www.protocols.io/api/v3/oauth/clients/{client_id}'
    response = requests.get(client_request_endpoint, headers=headers)

def request_token(client_id, client_secret):
    data = {
      'client_id': client_id,
      'client_secret': client_secret,
      'grant_type': 'authorization_code',
      'code': '<code>'
    }
    response = requests.post('https://www.protocols.io/api/v3/oauth/token', data=data)

get_protocol('22980', access_token)
create_protocol('28C5E0F0D96211E9A8EB9746B7AE966Ф', access_token)
