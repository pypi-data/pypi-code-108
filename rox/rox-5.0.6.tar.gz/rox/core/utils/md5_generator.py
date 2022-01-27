import json
import hashlib

def generate(properties, relevant_props):
    values = []
    for pt in relevant_props:
        if pt.name in properties:
            value_to_add = str(properties[pt.name]) #list and dict converts well to strings in python
            values.append(value_to_add)
    value_bytes = '|'.join(values).encode('utf-8')
    m = hashlib.md5()
    m.update(value_bytes)
    hash = m.hexdigest()

    return hash.upper()