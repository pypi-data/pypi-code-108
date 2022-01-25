async def modify(hub, name, chunk):
    """
    Take the given run name and low chunk, and allow state plugins to modify
    the low chunk
    """
    for mod in hub.idem.mod:
        if mod.__name__ == "init":
            continue
        if hasattr(mod, "modify"):
            chunk = mod.modify(name, chunk)
            chunk = await hub.pop.loop.unwrap(chunk)
    return chunk
