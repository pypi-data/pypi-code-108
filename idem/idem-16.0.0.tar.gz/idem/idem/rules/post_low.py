import copy


def check(hub, name, ctx, condition, req_ret, chunk):
    """
    If changes are made then run the configured post command
    """
    ret = {}
    if req_ret["ret"]["changes"]:
        id_ = f"{chunk['__id__']}_listen"
        post_chunk = copy.deepcopy(chunk)
        post_chunk["fun"] = condition
        post_chunk["__id__"] = id_
        post_chunk["name"] = id_
        post_chunk["order"] = -1
        hub.idem.RUNS[name]["post_low"].append(post_chunk)
    return ret
