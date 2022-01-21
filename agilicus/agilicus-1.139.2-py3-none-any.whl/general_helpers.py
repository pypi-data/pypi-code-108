def find_item(items, key, keyval):
    for item in items:
        if item[key] == keyval:
            return item
    return None


def find_object(items, key, keyval):
    for item in items:
        if getattr(item, key, None) == keyval:
            return item
    return None
