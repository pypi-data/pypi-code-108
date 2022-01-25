def stage(hub, name):
    """
    Apply the exclude value
    """
    high = hub.idem.ccomps.exclude.apply(hub.idem.RUNS[name]["high"])
    hub.idem.RUNS[name]["high"] = high
