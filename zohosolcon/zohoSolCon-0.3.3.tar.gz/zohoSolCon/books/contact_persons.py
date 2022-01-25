import requests
import json


def format_header(token):
    return {
        "Authorization": "Zoho-oauthtoken {token.access}"
    }


def create_contact_person(token, org_id, contact_id, data_object):
    url = f'https://books.zoho.com/api/v3/contacts/contactpersons?organization_id={org_id}'
    headers = format_header(token)

    data_object['contact_id'] = contact_id

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return create_contact_person(token, org_id, contact_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        try:
            contact_person = content['contact_person']['contact_person'][0]

        except Exception as e:
            contact_person = {'status': response.status_code, "error": str(e)}

        return token, response.status_code, contact_person



def update_contact_person(token, org_id, contact_person_id, data_object):
    url = f'https://books.zoho.com/api/v3/contacts/contactpersons/{contact_person_id}?organization_id={org_id}'
    headers = format_header(token)

    

    data = json.dumps(data_object).encode('utf-8')

    response = requests.put(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return create_contact_person(token, org_id, contact_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        try:
            contact_person = content['contact_person']['contact_person'][0]

        except Exception as e:
            contact_person = {'status': response.status_code, "error": str(e)}

        return token, response.status_code, contact_person



def delete_contact_person(token, org_id, contact_person_id):
    url = f'https://books.zoho.com/api/v3/contacts/contactpersons/{contact_person_id}?organization_id={org_id}'
    headers = format_header(token)

    response = requests.delete(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return delete_contact_person(token, org_id, contact_person_id)

    else:
        content = json.loads(resonse.content.decode('utf-8'))
        return token, content['message']


def get_contact_persons(token, org_id, contact_id, **kwargs):
    url = f'https//books.zoho.com/api/v3/contacts/{contact_id}/contactpersons?organization_id={org_id}'
    headers = format_header(token)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return get_contact_persons(token, org_id, contact_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
    try:
        pass
    except Exception as e:
        pass
    pass


