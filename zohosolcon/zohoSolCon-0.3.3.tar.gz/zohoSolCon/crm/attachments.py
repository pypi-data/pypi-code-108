import requests
import json


def get_attachments(token, module, record_id, **kwargs):
    url = f'https://www.zohoapis.com/crm/v2/{module}/{record_id}/Attachments'
    headers = {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_attachments(token, module, record_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")



