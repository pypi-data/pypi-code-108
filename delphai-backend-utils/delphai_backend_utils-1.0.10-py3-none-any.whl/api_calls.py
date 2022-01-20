import requests
import json
import logging


def call_azure_endpoint(api_url, api_key, request, max_timeouts=3, timeout_time=1.2):
    """
    Wrapper to call an Azure Machine Learning endpoint which also handles timeouts and errors.
    """
    response = {
        'content': None,
        'success': False,
        'original_response': None,
    }
    request_data = json.dumps(request)
    # Set the content type
    headers = {'Content-Type': 'application/json'}
    # If authentication is enabled, set the authorization header
    headers['Authorization'] = f'Bearer {api_key}'
    resp = None
    while (resp is None or resp.text is None) and max_timeouts >= 0:
        try:
            resp = requests.post(api_url, request_data, headers=headers, timeout=timeout_time)
        except requests.exceptions.Timeout:
            logging.warning(f'Request to {api_url} timed out (TimeOut)...')
        except requests.exceptions.ConnectionError:
            logging.warning(f'Request to {api_url} timed out (ConnectionError)...')
        max_timeouts -= 1

    if resp is None or resp.text is None or resp.status_code >= 400:
        response['original_response'] = resp
        return response
    else:
        response = {
            'content': json.loads(resp.text),
            'success': True,
            'original': resp,
        }
        return response
