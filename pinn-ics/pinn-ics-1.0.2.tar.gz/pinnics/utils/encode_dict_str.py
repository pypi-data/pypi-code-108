def encode_dict_str(dic):
    result = ""
    key_value = dic.items()
    for index, (key, value) in enumerate(key_value):
        if isinstance(value, int):
            value = float(value)
        result += str(key) + "_" + str(value)
        if index != len(key_value) - 1:
            result += "_"
    return result
