async def modify(hub, name, chunk):
    """
    Check the state containing the target func and call the aggregate
    function if present
    """
    func = hub.idem.rules.init.get_func(name, chunk, "mod_aggregate")
    if func:
        chunk = func(name, chunk)
        chunk = await hub.pop.loop.unwrap(chunk)
    return chunk
