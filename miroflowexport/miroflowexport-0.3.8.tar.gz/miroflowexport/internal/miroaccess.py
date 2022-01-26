import requests
import json

from miroflowexport.internal import plan
from miroflowexport.internal import transform

def get_board_url(log, board_id):
    url = "https://api.miro.com/v1/boards/{id}/".format(id = board_id)
    return url

def get_widgets_url(log, board_id):
    url = "https://api.miro.com/v1/boards/{id}/widgets/".format(id = board_id)
    return url


def get_headers(log, token):
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {token}".format(token = token)
    }
    return headers

def is_response_ok(log, response):
    if not response.ok:
        log.error(response.text)
        return False

    return True

def send_request(log, token, url):
    log.debug("Sending request to URL: {}".format(url))
    headers = get_headers(log, token)
    response = requests.request("GET", url, headers=headers)
    log.debug("Response status: {}".format(response.status_code))
    return response

def send_request_board(log, token, board_id):
    url = get_board_url(log, board_id)
    return send_request(log, token, url)

def send_request_widgets(log, token, board_id):
    url = get_widgets_url(log, board_id)
    return send_request(log, token, url)

def is_response_content_ok(log, response_dict):
    if not "data" in response_dict.keys():
        log.error("Cannot find 'data' property in response.")
        return False

    data = response_dict["data"]
    if not isinstance(data, list):
        log.error("Data property is not a list, but {}.".format(type(data)))
        return False

    return True


def get_list_of_cards(log, response_json):
    response_dict = json.loads(response_json)
    if not is_response_content_ok(log, response_dict):
        log.error("Cannot interpret response.")
        return []

    data_list_of_dicts = response_dict["data"]
    result = transform.filter_json_to_supported_task_types(log, data_list_of_dicts)
    log.info("Received {} task entry notes.".format(len(result)))
    return plan.create_tasks(log, result)

def get_list_of_dependencies(log, response_json, tasks):
    response_dict = json.loads(response_json)
    if not is_response_content_ok(log, response_dict):
        log.error("Cannot interpret response.")
        return []

    data = response_dict["data"]
    links = [
        entry
        for entry in data
        if entry["type"] == "line"
    ]    
    dependencies = transform.create_pairs_from_link_widgets(log, tasks, links)
    plan.add_task_dependencies(log, dependencies)
    log.info("Received {} dependencies.".format(len(dependencies)))