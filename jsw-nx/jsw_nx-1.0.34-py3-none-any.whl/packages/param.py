def param(in_dict):
    res = []
    for key in in_dict.keys():
        res.append(str(key) + '=' + str(in_dict[key]))
    return '&'.join(res)
