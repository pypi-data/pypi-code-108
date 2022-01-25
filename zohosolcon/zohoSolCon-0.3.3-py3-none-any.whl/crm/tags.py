import requests
import json


def get_tags(token, **kwargs):
    url = 'https://www.zohoapis.com/crm/v2/settings/tags'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_tags(token, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('tags')

def tag_record(token, module, record_id, tag_list, over_write=True):
    url = f'https://www.zohoapis.com/crm/v2.1/{modules}/actions/add_tags?ids={record_id}&tag_names='
    for tag in tag_list:
        if tag == tag_list[-1]:
            url += tag
        else:
            url += tag + ','
        if over_write:
            url += "&over_write=true"
        else:
            url += '&over_write=false'
            
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.post(url=url, headers=headers)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return tag_record(token, module, record_id, tag_list, over_write=over_write)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def remove_tags(token, module, record_id, tag_list):
    url = f'https://www.zohoapis.com/crm/v2.1/{modules}/actions/remove_tags?ids={record_id}&tag_names='
    for tag in tag_list:
        if tag == tag_list[-1]:
            url += tag
        else:
            url += tag + ','

    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.post(url=url, headers=headers)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return tag_record(token, module, record_id, tag_list, over_write=over_write)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def count_record_tags(token, module, tag_id):
    url = f'https://www.zohoapis.com/crm/v2/settings/{tag_id}/actions/records_count'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    parameters = {'module': module}

    response = requests.get(url=url, headers=headers, params=parameters)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return count_record_tags(token, module, tag_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, int(content.get('count'))


