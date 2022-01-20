import requests 
import json


def get_record(token, module, record_id):
    url = f"https://www.zohoapis.com/crm/v2.1/{module}/{record_id}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 400:
        print("Authentication issue")
        token.generate()
        return get_record(token, module, record_id)

    else:
        json_content = json.loads(response.content.decode('utf-8'))
        data = json_content['data'][0]
        return token, data


def update_record(token, module, record_id, data_object):
    url = f"https://www.zohoapis.com/crm/v2.1/{module}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }
    data_object["id"] = record_id

    request_body = dict()
    record_list = list()

    record_list.append(data_object)
    request_body['data'] = record_list

    data = json.dumps(request_body).encode('utf-8')
    response = requests.put(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth issue")
        token.generate()
        return update_record(token, module, record_id, data_object)

    else:
        return token, response.status_code, json.loads(response.content.decode('utf-8'))


def create_record(token, module, data_object):
    url = f"https://www.zohoapis.com/crm/v2.1/{module}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }
    request_body = {}
    record_list = [data_object]
    request_body['data'] = record_list

    data = json.dumps(request_body).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return create_record(token, module, data_object)

    else:
        return token, response.status_code, json.loads(response.content.decode('utf-8'))


def get_records(token, module, **kwargs):
    url = f"https://www.zohoapis.com/crm/v2.1/{module}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_records(token, module, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        records = content.get('data')

        return token, records


def search_records(token, module, criteria, **kwargs):
    url = f"https://www.zohoapis.com/crm/v2.1/{module}/search"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }

    parameters = {"criteria":criteria}

    parameters.update(kwargs)

    response = requests.get(url=url, headers=headers, params=parameters)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return search_records(token, module, criteria, **kwargs)

    elif response.status_code >= 300:
        raise Exception("Error in response {}".format(response.status_code))

    else:
        content = json.loads(response.content.decode('utf-8'))
        records = content.get('data')
        return token, records


def mass_action(token, module, callback, **kwargs):
    empty = False
    url = f"https://www.zohoapis.com/crm/v2.1/{module}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }
    page = 1
    iterated = 0
    parameters = kwargs
    while not empty:
        parameters['page'] = str(page)
        parameters['per_page'] = "200"
        response = requests.get(url=url, headers=headers, params=parameters)
        if response.status_code == 400:
            token.generate()
            headers = {
                "Authorization": f"Zoho-oauthtoken {token.access}"
            }
            continue
        content = json.loads(response.content.decode('utf-8'))
        data = content.get("data")

        if len(data) == 0:
            print("Done")
            empty = True

        for record in data:
            token, callback_response = callback(token, module, record)
            print(callback_response)
            iterated += 1
            print(f"{iterated} Records iterated")

        page += 1
        if len(data) < 200:
            empty = True

    return token, f"{iterated} Records iterated."



