import pop.loader


# These are keywords passed to state module functions which are to be used
# by salt in this state module and not on the actual state module function
STATE_REQUISITE_KEYWORDS = frozenset(
    [
        "onchanges",
        "onchanges_any",
        "onfail",
        "onfail_any",
        "onfail_all",
        "onfail_stop",
        "prereq",
        "prerequired",
        "watch",
        "watch_any",
        "require",
        "require_any",
        "listen",
        "arg_bind",
    ]
)
STATE_REQUISITE_IN_KEYWORDS = frozenset(
    [
        "onchanges_in",
        "onfail_in",
        "prereq_in",
        "watch_in",
        "require_in",
        "listen_in",
    ]
)
STATE_RUNTIME_KEYWORDS = frozenset(
    [
        "fun",
        "state",
        "check_cmd",
        "failhard",
        "onlyif",
        "unless",
        "retry",
        "order",
        "parallel",
        "prereq",
        "prereq_in",
        "prerequired",
        "reload_modules",
        "reload_grains",
        "reload_pillar",
        "runas",
        "runas_password",
        "fire_event",
        "saltenv",
        "use",
        "use_in",
        "__run_name",
        "__env__",
        "__sls__",
        "__id__",
        "__orchestration_jid__",
        "__pub_user",
        "__pub_arg",
        "__pub_jid",
        "__pub_fun",
        "__pub_tgt",
        "__pub_ret",
        "__pub_pid",
        "__pub_tgt_type",
        "__prereq__",
    ]
)

STATE_INTERNAL_KEYWORDS = STATE_REQUISITE_KEYWORDS.union(
    STATE_REQUISITE_IN_KEYWORDS
).union(STATE_RUNTIME_KEYWORDS)


def get_func(hub, name, chunk, fun=None):
    """
    Given the runtime name and the chunk in question, determine what function
    on the hub that can be run
    """
    if fun is None:
        fun = chunk["fun"]
    s_ref = chunk["state"]

    # Check if an auto_state exists for this ref
    try:
        if "auto_state" in hub.exec[s_ref].__contracts__:
            chunk["exec_mod_ref"] = s_ref
            return hub.states.auto_state[fun]
    except AttributeError or TypeError:
        ...
    for sub in hub.idem.RUNS[name]["subs"]:
        test = f"{sub}.{s_ref}.{fun}"
        try:
            func = getattr(hub, test)
        except AttributeError:
            continue
        if isinstance(func, pop.loader.LoadedMod):
            continue
        if func is None:
            continue
        return func
    return None


async def run(hub, name, ctx, low, seq_comp, running, run_num):
    """
    All requisites have been met for this low chunk.
    """
    chunk = seq_comp["chunk"]
    tag = hub.idem.tools.gen_tag(chunk)
    skip_check = ["resolver"]
    rdats = {}
    errors = []
    for reqret in seq_comp.get("reqrets", []):
        req = reqret["req"]
        if req not in rdats:
            rdats[req] = []
        rules = hub.idem.RMAP[req]
        for rule in rules:
            if rule in skip_check:
                continue
            if hasattr(hub.idem.rules, rule):
                rdat = getattr(hub.idem.rules, rule).check(
                    name, ctx, rules[rule], reqret, chunk
                )
                rdats[req].append(rdat)
    errors = hub.idem.resolver.init.resolve(rdats)
    if errors:
        running[tag] = {
            "name": chunk["name"],
            "changes": {},
            "comment": "\n".join(errors),
            "result": False,
            "__run_num": run_num,
        }
        return
    func = hub.idem.rules.init.get_func(name, chunk)
    if func is None:
        running[tag] = {
            "name": chunk["name"],
            "changes": {},
            "comment": f'Could not find function to enforce {chunk["state"]}.'
            f"Please make sure that the corresponding plugin is loaded.",
            "result": False,
            "__run_num": run_num,
        }
        return
    chunk["ctx"] = ctx
    chunk = await hub.idem.mod.init.modify(name, chunk)
    call = hub.idem.tools.format_call(
        func, chunk, expected_extra_kws=STATE_INTERNAL_KEYWORDS
    )
    for req, rlist in rdats.items():
        for rdat in rlist:
            if "pre" in rdat:
                ret = rdat["pre"](*call["args"], **call["kwargs"])
                await hub.pop.loop.unwrap(ret)
    ret = func(*call["args"], **call["kwargs"])
    ret = await hub.pop.loop.unwrap(ret)
    for req, rlist in rdats.items():
        for rdat in rlist:
            if "post" in rdat:
                ret = rdat["post"](*call["args"], **call["kwargs"])
                ret = await hub.pop.loop.unwrap(ret)
    ret["__run_num"] = run_num
    running[tag] = ret
