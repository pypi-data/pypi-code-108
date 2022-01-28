"""Set value from kwargs, falling back to default.
Gives some flexibility for keynames.
"""
def parse_kw(lbl_in, kwargs, default=None):
    for key in lbl_in:
        if key in kwargs.keys():
            return kwargs[key]
    return default
