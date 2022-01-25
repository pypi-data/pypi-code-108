def req_map(hub):
    """
    Gather the requisite restrictions and populate the requisite behavior map
    """
    rmap = {}
    for mod in hub.idem.req:
        if mod.__name__ == "init":
            continue
        if hasattr(mod, "define"):
            rmap[mod.__name__] = mod.define()
    hub.idem.RMAP = rmap
