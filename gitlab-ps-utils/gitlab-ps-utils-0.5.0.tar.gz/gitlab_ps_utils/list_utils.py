

def safe_list_index_lookup(l, v):
    """
        Helper method to safely lookup the index of a list based on a specific value
    """
    return l.index(v) if v in l else None


def remove_dupes(my_list):
    """
        Basic deduping function to remove any duplicates from a list
    """
    return list({v.get("id"): v for v in my_list}.values())


def remove_dupes_with_keys(my_list, list_of_keys):
    """
        Deduping function to remove any duplicates from a list based on a set of keys
    """
    d = {}
    for v in my_list:
        key = ""
        for k in list_of_keys:
            key += str(v.get(k, ""))
        d[key] = v
    return list(d.values())
