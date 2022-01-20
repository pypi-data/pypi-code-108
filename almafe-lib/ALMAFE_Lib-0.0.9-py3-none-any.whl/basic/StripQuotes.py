'''
Utility to strip quotes from a string, if present.
'''

def stripQuotes(string):
    if string.startswith("'") and string.endswith("'"):
        string = string[1:-1]
    elif string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string