import requests
import json


def get_roles(token):
    url = 'https://www.zohoapis.com/crm/v2.1/settings/roles'
    headers = {'Authorization': f'Zoho-oauthtoken {token.access}'}

    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return get_roles(token)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("roles")


def get_role(token, role_id):
    url = f'https://www.zohoapis.com/crm/v2.1/settings/roles/{role_id}'
    headers = {'Authorization': f'Zoho-oauthtoken {token.access}'}

    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return get_role(token, role_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("roles")



