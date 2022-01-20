import requests
import json


def get_notes(token, **kwargs):
    url = 'https://www.zohoapis.com/crm/v2/Notes'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_notes(token, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")


def get_note(token, note_id):
    url = f'https://www.zohoapis.com/crm/v2/Notes/{note_id}'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_note(token, note_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def get_record_notes(token, module, record_id, **kwargs):
    url = f'https://www.zohoapis.com/crm/v2/{module}/{record_id}/Notes'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_record_notes(token, module, record_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def create_note(token, module, record_id, note_object):
    url = 'https://www.zohoapis.com/crm/v2/Notes'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }

    request_body = {}
    note_object['Parent_Id'] = record_id
    note_object['se_module'] = module
    note_list = [note_object]

    request_body['data'] = record_list

    data = json.dumps(request_body).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if resonse.status_code == 400:
        print("Auth")
        token.generate()
        return create_note(token, module, record_id, note_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content



