import json

def clear_headers(headers):
    headers_keys = []
    [headers_keys.append(key) for key in headers.keys()]
    for key in headers_keys:
        if 'CloudFront' in key or 'Accept' in key or 'Forwarded' in key or 'Amz' in key or 'Host' in key or 'Via' in key or 'User-Agent' in key or 'content-type' in key:
            del(headers[key])
    return headers

def get_data_from_event(event, is_batch=False):
    """ extract data from event, considering:
        - local execution
        - apiGateway (POST, GET)
        - Queues: firs row.body in records
    """
    data = event # by default data is whole event (local execution)
    data = event["body"] if "body" in event and event["body"] else event # if is a POST, data is body
    data = event["query"] if "query" in event and event["query"] else data # if is a GET, data is query
    if is_batch:
        data = [data]

    if("Records" in event and len(event["Records"]) and "body" in event["Records"][0] and event["Records"][0]["body"]): # if is from queue, data is BODY in first records
        if is_batch:
            data = [x["body"] for x in event["Records"]]
        else:
            data = event["Records"][0]["body"]
    ## try to converto to json, if it fails, will return data retrieved from event, body or query.
    try:
        data = [json.loads(x) for x in data] if is_batch else json.loads(data)
    except:
        pass
    if 'headers' in event:
        if type(data) == list:
            for message in data:
                message['headers']= clear_headers(event['headers'])
        else:
            data['headers'] = clear_headers(event['headers'])
    return data

def is_from_queue(event):
    """ return True if message comes from queue """
    if("Records" in event and len(event["Records"]) and "body" in event["Records"][0] and event["Records"][0]["body"]):
        return True
    else:
        return False

def get_claims(event, name):
    if "cognitoPoolClaims" not in event:
        raise Exception("cognitoPoolClaims not defined in event")
    ev = event["cognitoPoolClaims"]
    if name not in ev:
        raise Exception("{} not found in claims, make sure it's configured in lambda claims".format(name))
    return ev.get(name)