"""Methods to parse string patterns."""
from operator import attrgetter


def _join_parent_attrs(
        obj, parent_path, val_path, sep=' / ', _reversed=True):
    # TODO: do we need to handle Falsy values in some special way?
    def get_next_val(parent):
        parent_f = attrgetter(parent_path)
        val_f = attrgetter(val_path)
        while parent:
            # Convert to string is needed when non string value is
            # present.
            yield str(val_f(parent))
            parent = parent_f(parent)
    vals_lst = [val for val in get_next_val(obj)]
    if _reversed:
        vals_lst = reversed(vals_lst)
    return ('%s' % sep).join(vals_lst)
