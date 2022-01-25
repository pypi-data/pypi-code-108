def resolve(hub, rdats):
    """
    Given the dict of requisite data sets, determine if the defined
    requisites passed. This allows for requisites to be defined
    as requiring, all, some, one, or none of the required states to
    pass
    """
    errors = []
    for req, rlist in rdats.items():
        rmap = hub.idem.RMAP[req]
        resolver = rmap.get("resolver", "all")
        errors.extend(getattr(hub, f"idem.resolver.{resolver}.check")(rlist))
    return errors
