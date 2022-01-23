def getDictFromString(string: str):
    response = {}
    keyValues = list(map(lambda x: x.strip(), string.split(';')))
    for pair in keyValues:
        key, value = pair.split('=')
        response.update({key: value})
    return response
