"""Tools for the Extender Python environment."""
try:
    from accpac import program
except ImportError:
    program = ""

EXEC_VI = 0
"""Extender Execution Context"""
EXEC_PS = 1
"""Process Sceduler Execution Context"""

def execution_context():
    """Are we running through PS or VI?

    :returns: ``EXEC_PS`` if PS else ``EXEC_VI``
    """
    if program.startswith("AS1"):
        return EXEC_PS
    return EXEC_VI
