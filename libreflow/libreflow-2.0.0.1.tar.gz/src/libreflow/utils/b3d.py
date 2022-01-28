import platform


def wrap_python_expr(expression):
    '''
    This functions wraps python expression for b3d within an exec()
    as windows shells are not handling well the line breaks
    '''
    _os = platform.system()
    if _os == "Windows":
        expression = 'exec(%s)' % repr(expression)
    return expression