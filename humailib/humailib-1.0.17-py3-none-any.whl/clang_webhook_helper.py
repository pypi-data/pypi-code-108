import requests

def CreateWebhookEmail(name, email, newsletter=False):
    request_body = '{{\"firstname\":\"{0}\",\"prefix\":\"{1}\",\"surname\":\"{2}\",\"email\":\"{3}\",\"newsletter\":\"{4}\"}}'.format(name[0], name[1], name[2], email, "yes" if newsletter else "no")
    return request_body

def CreateJSONFromEmailsGroupsSenddays(emails, groups, sendday):
    json = '{\n\"contacts\": [\n'
    
    i = 0
    
    for e,g,s in zip(emails,groups,sendday):
        
        entry = '{{\n\"email\": \"{0}\",\n\"controlgroup\": \"{1}\",\n\"sendday\":\"{2}\"\n}}'.format(e,g,s)
        if i < (len(emails)-1):
            entry = entry + ','
        
        json = json + entry + '\n'
        
        i = 1 + i
    
    json = json + ']\n}'
    
    return json
    
def SendWebhookRequest(url, json, verbose=False):
    response = requests.post(url, data=json)
    if verbose:
        print("Response code: {0}".format(response.status_code))
        print("Response: " + response.text)

    return response.status_code