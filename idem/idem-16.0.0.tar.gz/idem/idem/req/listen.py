def define(hub):
    """
    Return the definition used by the runtime to insert the conditions of the
    given requisite
    """
    return {
        "post_low": "mod_watch",
        "resolver": "any",
    }
