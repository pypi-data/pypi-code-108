import sys
from string import Formatter
from collections import OrderedDict

from kabaret.flow_contextual_dict import get_contextual_dict


def keywords_from_format(format):
    return [fname for _, fname, _, _ in Formatter().parse(format) if fname]


def _get_param_values(leaf, name, level=0, max_level=sys.maxsize):
    session = leaf.root().session()
    param_oid = leaf.oid() + '/' + name
    values = []
    
    if session.cmds.Flow.exists(param_oid):
        value = session.cmds.Flow.get_value(param_oid)
        values.append(value)
    
    parent = leaf._mng.parent
    
    if parent is not leaf.root() and level < max_level:
        parent_values = _get_param_values(parent, name, level + 1, max_level)
        return parent_values + values
    else:
        return values


def get_context_value(
        leaf,
        param_name,
        delim='',
        context_name='settings',
        max_level=sys.maxsize,
    ):
    
    session = leaf.root().session()
    
    # Recursively search param
    param_values = _get_param_values(leaf, param_name, max_level=max_level)
    
    if not param_values:
        return None
    
    # Build context value from accumulated values
    context_value = delim.join(param_values)
    
    # Search for contextual keys
    try:
        keys = keywords_from_format(context_value)
    except ValueError:
        session.log_error((
            f"Invalid value format \"{context_value}\"\n\n"
            "<<<<<<<<<<< TRACEBACK >>>>>>>>>>\n"
        ))
        raise
    
    if keys:
        # Get contextual values
        context = get_contextual_dict(leaf, context_name)
        values = OrderedDict()
        
        for key in keys:
            try:
                values[key] = context[key]
            except KeyError:
                session.log_error((
                    f"No key \"{key}\" in {leaf.oid()} context\n\n"
                    "<<<<<<<<<<< TRACEBACK >>>>>>>>>>\n"
                ))
                raise
        
        context_value = context_value.format(**values)
    
    return context_value
