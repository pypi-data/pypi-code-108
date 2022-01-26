
def merge_role_key(key, role):
        return role + '.' + key

def split_role_key(label_key):
        split = label_key.split('.')
        role = split[0]
        key = '.'.join(split[1:])
        return role, key
