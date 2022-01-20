import requests
import json


def get_contact(token, org_id, contact_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_contact(token, org_id, contact_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def get_contacts(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/contacts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_contacts(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")


def create_contact(token, org_id, data_object):
    url = 'https://desk.zoho.com/api/v1/contacts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }

    data = json.dumps(data_object).encode('utf-8')
    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return create_contact(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def update_contact(token, org_id, contact_id, data_object):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    data = json.dumps(data_object).encode('utf-8')
    
    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return update_contact(token, org_id, contact_id, data_object)

    else:
        content =json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def contact_tickets(token, org_id, contact_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}/tickets'
    headers = {
        'orgId':org_id,
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return contact_tickets(token, org_id, contact_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def contact_products(token, org_id, contact_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}/products'
    headers = {
        'orgId':org_id,
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)
    if response.status_code == 400:
        print("Auth")
        token.generate()
        return contact_products(token, org_id, contact_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def contacts_count(token, org_id, view_id):
    url = 'https://desk.zoho.com/api/v1/contacts/count'
    headers = {
        'orgId':org_id,
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params={'viewId':view_id})

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return contacts_count(token, org_id, view_id)
    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, int(content.get('count'))


def contact_stats(token, org_id, contact_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}/statistics'
    headers = {
        'orgId':org_id,
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)
    
    if response.status_code == 400:
        print("Auth")
        token.generate()
        return contact_status(token, org_id, contact_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def contact_product_link(token, org_id, contact_id, product_id_list, associate=True, department_id=None):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}/associateProducts'
    headers = {
        'orgId':org_id,
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }
    data_object = {"ids": product_id_list, 'associate': associate}

    data = json.dumps(data_object).encode('utf-8')
    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print('Auth')
        token.generate()
        return contact_product_link(token, org_id, contact_id, product_id_list, associate=associate)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content.get('results')


def contact_accounts(token, org_id, contact_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/contacts/{contact_id}/accounts'
    headers = {
        'orgId':org_id,
        "Authorization": f'Zoho-oauthtoken {token.access}'
    }

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return contact_accounts(token, org_id, contact_id, **kwargs)

    else:
        content =json.loads(response.content.decode('utf-8'))

        return token, content.get('data')





    
