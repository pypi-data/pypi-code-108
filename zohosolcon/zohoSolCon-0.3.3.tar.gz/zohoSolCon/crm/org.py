import requests
import json


def get_org_details(token):
    url = "https://www.zohoapis.com/crm/v2.1/org"

    headers = {
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }
    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        token.generate()
        return get_org_details(token)

    else:
        content = json.loads(response.content.decode('utf-8'))
        org = content.get("org")
        return token, org


