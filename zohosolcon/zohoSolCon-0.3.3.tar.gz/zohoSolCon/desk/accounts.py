import requests
import json


def get_account(token, org_id, account_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return get_account(token, org_id, account_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def get_accounts(token, org_id, **kwargs):
    url = f'https://desk.zoho.com/v1/accounts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return get_accounts(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def create_account(token, org_id, data_object):
    url = f'https://desk.zoho.com/v1/accounts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return create_account(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content

def update_account(token, org_id, data_object):
    url = f'https://desk.zoho.com/v1/accounts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }

    data = json.dumps(data_object).encode('utf-8')
    
    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        return update_account(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def account_contracts(token, org_id, account_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}/contracts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return account_contracts(token, org_id, account_id, **kwargs)

    else:
        return token, json.loads(response.content.decode('utf-8')).get('data')


def accounts_count(token, org_id, view_id):
    url = 'https://desk.zoho.com/api/v1/accounts/count'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params={'viewId': view_id})

    if response.status_code == 400:
        token.generate()
        return accounts_count(token, org_id, view_id)

    else:
        return token, int(json.loads(response.content.decode('utf-8')).get('count'))


def account_contacts(token, org_id, account_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}/contacts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return account_contacts(token, org_id, account_id, **kwargs)

    else:
        return token, json.loads(response.content.decode('utf-8')).get('data')


def account_tickets(token, org_id, account_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}/tickets'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return account_tickets(token, org_id, account_id, **kwargs)

    else:
        return token, json.loads(response.content.decode('utf-8')).get('data')


def account_products(token, org_id, account_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}/products'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        token.generate()
        return account_products(token, org_id, account_id, **kwargs)

    else:
        return token, json.loads(response.content.decode('utf-8')).get('data')


def account_product_link(token, org_id, account_id, product_id_list, associate=True):
    url = f'https://desk.zoho.com/api/v1/accounts/{account_id}/associateProducts'
    headers = {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    data_object = {'ids': product_id_list, 'associate': associate}

    data = json.dumps(data_object).encode('utf-8')
    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        token.generate()
        
        return account_product_link(token, org_id, account_id, product_id_list, associate=associate)

    else:
        return token, response.status_code, json.loads(response.content.decode('utf-8')).get('results')


