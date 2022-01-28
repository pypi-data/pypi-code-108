def get_NoneStr(str):
    if str is None:
        return ''
    else:
        return str


def get_NullStr(str):
    if str is None:
        return ''
    elif str == 'null':
        return ''
    else:
        return str

def StrToBytes(mystring):
    if isinstance(mystring, str):
        return mystring.encode('utf-8')
    else:
        raise Exception(f'{mystring} must be str')


def BytesToStr(mybytes):
    if isinstance(mybytes, bytes):
        return mybytes.decode('utf-8')
    else:
        raise Exception(f'{mybytes} must be bytes')
