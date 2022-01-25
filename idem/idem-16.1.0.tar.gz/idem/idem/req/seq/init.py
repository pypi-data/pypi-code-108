def seq(hub, low, running):
    """
    Process the multi stage routine to determine the current requisite sequence
    """
    # TODO: Make this more pluggable. This means that plugins get detected and run,
    # Granted, we only need to do this for prereq, I don't think that we will need
    # to add another plugin here.
    ret = hub.idem.req.seq.straight.run(low, running)
    ret = hub.idem.req.seq.prereq.run(ret, low, running)
    return ret
