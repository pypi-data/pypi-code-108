"""equal operation"""


def equal(obj1, obj2):
    """Check if two JSON objects are equal.
    :param obj1 first JSON object
    :param obj2 second JSON object
    :return True if obj1 == obj2
    """
    if type(obj1) != type(obj2):
        return obj1 == obj2
    if isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False
        for k in obj1:
            if k not in obj2 or not equal(obj1[k], obj2[k]):
                return False
        return True
    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False
        marks = [0 for _ in range(len(obj2))]
        for s1 in obj1:
            found = False
            for i in range(len(obj2)):
                if marks[i] == 0 and equal(s1, obj2[i]):
                    found = True
                    marks[i] = 1
                    break
            if not found:
                return False
        return True
    else:
        return obj1 == obj2


