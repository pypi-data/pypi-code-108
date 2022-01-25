import copy


def check(hub, name, ctx, condition, reqret, chunk):
    """
    Check to see if the reqret state will make changes in the future
    """
    # condition = "changes"
    # First, prepare the ctx for the reqret chunk
    # Execute the reqret chunk in test mode
    # if the condition returns True then no errors are presented
    ret = {"errors": []}
    ctx = copy.deepcopy(ctx)
    ctx["test"] = True
    r_chunk = copy.deepcopy(reqret["chunk"])
    func = hub.idem.rules.init.get_func(name, r_chunk)
    r_chunk["ctx"] = ctx
    call = hub.idem.tools.format_call(
        func, r_chunk, expected_extra_kws=hub.idem.rules.init.STATE_INTERNAL_KEYWORDS
    )
    sret = func(*call["args"], **call["kwargs"])
    cond = sret.get(condition, False)
    if not cond:
        ret["errors"].append(
            f"No {condition} found in execution of {reqret['state']}.{reqret['name']}"
        )
    return ret
