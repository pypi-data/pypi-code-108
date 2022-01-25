"""
This plugin is used to resolve transparent requisites and apply them to
the lowstate

.. code-block:: python

    TREQ = {
        "func_D": {
            "require": [
                "foo.bar.baz.func_A",
                "test.func_B",
            ],
            "soft_require": [
                "cheese.func_C",
            ],
        }
    }
"""
import pop.loader


def gather(hub, subs, low):
    """
    Given the runtime name and the chunk in question, determine what function
    on the hub that can be run
    """
    ret = {}
    for chunk in low:
        s_ref = chunk["state"]
        if s_ref in ret:
            continue
        for sub in subs:
            test = f"{sub}.{s_ref}"
            try:
                mod = getattr(hub, test)
            except AttributeError:
                continue
            if not isinstance(mod, pop.loader.LoadedMod):
                continue
            if mod is None:
                continue
            if hasattr(mod, "TREQ"):
                ret.update({s_ref: mod.TREQ})
    return ret


def apply(hub, subs, low):
    """
    Look up the transparent requisites as defined in state modules and apply
    them to the respective low chunks
    """
    treq = hub.idem.ccomps.treq.gather(subs, low)
    for chunk in low:
        if not chunk["state"] in treq:
            continue
        if not chunk["fun"] in treq[chunk["state"]]:
            continue
        rule = treq[chunk["state"]][chunk["fun"]]
        for rule_name, rule_refs in rule.items():
            for ref in rule_refs:
                for req_chunk in low:
                    req_path = f'{req_chunk["state"]}.{req_chunk["fun"]}'
                    if req_path == ref:
                        if rule_name not in chunk:
                            chunk[rule_name] = []
                        chunk[rule_name].append(
                            {req_chunk["state"]: req_chunk["__id__"]}
                        )
    return low
