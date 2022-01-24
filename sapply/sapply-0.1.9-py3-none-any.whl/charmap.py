import json
import wora.file

def to_charmap(jstr: str) -> dict:
    '''Converts a json string to a charmap dictionary'''
    data = json.loads(jstr)
    return data

def read_charmap(conts: str) -> dict:
    return(to_charmap(wora.file.read_file(conts)))

# Convert character maps to json
def to_json(charmap: dict) -> str:
    ''' Converts a dictionary charmap to json '''
    o = json.dumps(charmap, indent=4, ensure_ascii=False) # Don't unescape Unicode characters
    return o

def export_charmap(charmap: dict, fname: str):
    wora.file.write_file(fname, to_json(charmap))
