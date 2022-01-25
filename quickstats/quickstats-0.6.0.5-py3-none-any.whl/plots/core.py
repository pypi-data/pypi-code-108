import ROOT

def set_attrib(obj, **kwargs):
    for key, value in kwargs.items():
        target = obj
        if '.' in key:
            tokens = key.split('.')
            if len(tokens) != 2:
                raise ValueError('maximum of 1 subfield is allowed but {} is given'.format(len(tokens)-1))
            field, key = tokens[0], tokens[1]
            method_name = 'Get' + field
            if hasattr(obj, 'Get' + field):
                target = getattr(obj, method_name)()
            else:
                raise ValueError('{} object does not contain the method {}'.format(type(target), method_name)) 
        method_name = 'Set' + key
        if hasattr(target, 'Set' + key):
            method_name = 'Set' + key
        elif hasattr(target, key):
            method_name = key
        else:
            raise ValueError('{} object does not contain the method {}'.format(type(target), method_name))         
        if value is None:
            getattr(target, method_name)()
        elif isinstance(value, (list, tuple)):
            getattr(target, method_name)(*value)
        else:
            getattr(target, method_name)(value)
    return obj