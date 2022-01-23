import json
from Cryptodome.Cipher import AES

# sys.path.append('../')
from .variables import *
from .decos import log_func

# @log_func
def get_message(client):
    '''
    The function of receiving messages from remote computers.
    Accepts JSON messages, decodes the received message
    and checks that the dictionary has been received.
    :param client: data transfer socket.
    :return: dictionary - message.
    '''
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


# @log_func
def send_message(sock, message):
    '''
    The function of sending dictionaries via socket.
    Encodes the dictionary in JSON format and sends it via socket.
    :param sock: socket for transmission
    :param message: dictionary for transmission
    :return: returns nothing
    '''
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
