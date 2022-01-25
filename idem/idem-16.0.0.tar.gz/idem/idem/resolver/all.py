def check(hub, rlist):
    """
    Chek the resolve list from the requisite systems and return errors from all
    errored requisites
    """
    errors = []
    for rdat in rlist:
        errors.extend(rdat.get("errors", []))
    return errors
