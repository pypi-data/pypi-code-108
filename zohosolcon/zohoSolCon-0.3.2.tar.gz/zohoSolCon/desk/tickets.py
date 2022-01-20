import requests
import json


def get_ticket(token, org_id, ticket_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/tickets/{}'.format(ticket_id)
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_ticket(token, org_id, ticket_id, **kwargs)

    else:
        data = json.loads(response.content.decode('utf-8'))
        return token, data


def get_tickets(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/tickets'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return get_tickets(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def create_ticket(token, org_id, data_object):
    url = 'https://desk.zoho.com/api/v1/tickets'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }

    data = json.dumps(data_object).encode("utf-8")
    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return create_ticket(token, org_id, data_object)
    

def update_ticket(token, org_id, ticket_id, data_object):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}'
    data = json.dumps(data_object).encode('utf-8')
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    response = requests.patch(url=url, headers=headers, data=data)
    if response.status_code == 400:
        print("Auth")
        token.generate()
        return update_ticket(token, org_id, ticket_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def trash_ticket(token, org_id, ticket_id_list):
    url = 'https://desk.zoho.com/api/v1/tickets/moveToTrash'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    
    data_object = {'ticketIds': ticket_id_list}

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return trash_ticket(token, org_id, ticket_id_list)

    else:
        return token, response.status_code


def move_ticket(token, org_id, ticket_id, department_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/move'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    data_object = {'departmentId': department_id}

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return move_ticket(token, org_id, ticket_id, department_id)

    else:
        return token, response.status_code


def mark_read(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/markAsRead'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    response = requests.post(url=url, headers=headers)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return mark_read(token, org_id, ticket_id)

    else:
        return token, response.status_code


def mark_unread(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/markAsUnRead'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    response = requests.post(url=url, headers=headers)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return mark_unread(token, org_id, ticket_id)

    else:
        return token, reponse.status_code


def ticket_history(token, org_id, ticket_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/History'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return ticket_history(token, org_id, ticket_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content.get('data')


def ticket_resolution(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/resolution'
    headers = {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {}'.format(token.access)
    }
    response = requests.get(url=url, headers=headers)

    if response.status_code == 400:
        print("Auth")
        token.generate()
        return ticket_resolution(token, org_id, ticket_id)

    
