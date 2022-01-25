import requests
import json


def format_header(token):
    return {
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }


def create_contact(token, org_id, data_object):
    url = f'https://books.zoho.com/api/v3/contacts?organization_id={org_id}'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return create_contact(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content.get("contact")


def get_contacts(token, org_id, **kwargs):
    url = f'https://books.zoho.com/api/v3/contacts?organization_id={org_id}'
    headers = format_header(token)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return get_contacts(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        try:
            contacts = content['contacts']
            page_context = content['page_context']

        except Exception as e:
            contacts = [{'status': response.status_code, 'error': str(e)}]
            page_context = None

        return token, page_context, contacts



def update_contact(token, org_id, contact_id, data_object):
    url = f'https://books.zoho.com/api/v3/contacts/{contact_id}?organization_id={org_id}'
    headers = format_header(token)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.put(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return update_contact(token, org_id, contact_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))

        try:
            contact = content['contact']
        except Exception as e:
            contact = {'status': response.status_code, 'error': str(e)}

        return token, response.status_code, contact


def get_contact(token, org_id, contact_id):
    url = f'https://books.zoho.com/api/v3/contacts/{contact_id}?organization_id={org_id}'
    headers = format_header(token)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return get_contact(token, org_id, contact_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        try:
            contact = content['contact']
        except Exception as e:
            contact = {'status': response.status_code, 'error': str(e)}

        return token, contact


def delete_contact(token, org_id, contact_id):
    url = f'https://books.zoho.com/api/v3/contacts/{contact_id}?organization_id={org_id}'
    headers = format_header(token)

    response = requests.delete(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return delete_contact(token, org_id, contact_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content['message']


def mark_status(token, org_id, contact_id, status):
    url = f'https://books.zoho.com/api/v3/contacts/{contact_id}/{status}?organization_id={org_id}'
    headers = format_header(token)

    response = requests.post(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return mark_status(token, org_id, contact_id, status)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content['message']


def grant_portal_access(token, org_id, contact_id, contact_person_ids):
    url = 'https://books.zoho.com/api/v3/contacts/{contact_id}/portal/enable?organization_id={org_id}'
    headers = format_header(token)

    data_object = {}
    contact_persons = []
    for id in contact_person_ids:
        obj = {"contact_person_id": id}
        contact_persons.append(obj)

    data_object['contact_persons'] = contact_persons

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return grant_portal_access(token, org_id, contact_id, contact_person_ids)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content['message']


def mass_action(token, org_id, callback, **kwargs):
    next_page = True
    page = 1
    iterated = 0
    parameters = kwargs
    while next_page:
        url = f'https://books.zoho.com/api/v3/contacts?organization_id={org_id}'
        headers = format_header(token)
        parameters['page'] = str(page)
        parameters['per_page'] = '200'

        response = requests.get(url=url, headers=headers, params=parameters)
        if response.status_code == 400:
            token.generate()
            continue

        content = json.loads(response.content.decode('utf-8'))
        contacts = content['contacts']

        for record in contacts:
            token, callback_response = callback(token, org_id, record)
            print(callback_response)
            iterated += 1
            print(f'{iterated} Records Iterated')

        page_context = content['page_context']
        page += 1
        next_page = page_context['has_more_page']
    return token, f'{iterated} Records Iterated \n=========\n Mass Operations Complete'



        

