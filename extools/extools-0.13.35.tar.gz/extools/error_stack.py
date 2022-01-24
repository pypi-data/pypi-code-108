"""Tools for working with the Sage Error Stack through Extender."""
try:
    from accpac import ErrorStack
except ImportError:
    pass

def consume_errors():
    """Consume the message on the stack and get them as (Pri, Msg) pairs.

    :returns: [(pri, msg), (pri, msg), ...]
    :rtype: list
    """
    errors = ErrorStack()
    output = [(errors.getPriority(i), errors.getText(i), )
              for i in range(0, errors.count())]
    errors.clear()
    return output
