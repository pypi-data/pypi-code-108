import json
import boonnano
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""a collection of methods to standardize/isolate http request/response"""

user_agent = 'Boon Logic / expert-python-sdk / urllib3'

def outgoing_data(response):
    if response.status != 200:
        if response.headers['Content-Type'] == 'application/json':
            if response.data.decode('utf-8') == '':
                decoded = {'code': response.status, 'message': "empty response"}
            else:
                decoded = json.loads(response.data.decode('utf-8'))
            if 'code' in decoded and 'message' in decoded:
                return False, '{}: {}'.format(decoded['code'], decoded['message'])
            return False, decoded
        else:
            return False, response.reason
    try:
        content_type = response.headers['Content-Type']
        if content_type == 'application/json':
            if response.data == b'':
                return True, '{}'
            return True, json.loads(response.data.decode('utf-8'))
        elif content_type == 'application/octet-stream':
            return True, response.data
        else:
            return False, "unhandled Content-Type: {}".format(content_type)

    except Exception as e:
        return False, e


def simple_get(nano_handle, get_cmd):
    try:
        response = nano_handle.http.request(
            'GET',
            get_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'Content-Type': 'application/json',
                'User-Agent': user_agent
            }
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    return outgoing_data(response)


def multipart_post(nano_handle, post_cmd, fields=None):

    try:
        response = nano_handle.http.request(
            'POST',
            post_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'User-Agent': user_agent
            },
            fields=fields
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    return outgoing_data(response)


def simple_post(nano_handle, post_cmd, body=None):
    try:
        response = nano_handle.http.request(
            'POST',
            post_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'Content-type': 'application/json',
                'User-Agent': user_agent
            },
            body=body
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    return outgoing_data(response)


def simple_delete(nano_handle, delete_cmd):
    try:
        response = nano_handle.http.request(
            'DELETE',
            delete_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'User-Agent': user_agent
            }
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    return outgoing_data(response)
