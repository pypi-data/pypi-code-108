from textwrap import fill
import click

FW = 80

def address(message, preformatted=False, list_format=False):
    """Addresses the user (e.g. a greeting or transition to the next step).
    This may be verbose, so text is wrapped.
    """
    if preformatted:
        if list_format: 
            raise ValueError("preformatted and list_format are incompatible options")
        fmsg = message
    elif list_format:
        fmsg = fill(message, width=FW, initial_indent='- ', subsequent_indent='  ')
    else:
        fmsg = fill(message, width=FW) + '\n'
    return click.style(fmsg, fg='cyan')

def question(message):
    """Addresses the user qith a question (e.g. a prompt)
    """
    return click.style(fill(message, width=FW) + '\n', fg="cyan")

def info(message, preformatted=False):
    """Shows the user information. 
    Don't use this for boilerplate; the user should have requested the information 
    or may need to check it.
    """
    if preformatted:
        return click.style(message, fg="blue")
    else:
        return click.style(fill(message, width=FW), fg="blue")

def warn(message):
    """Warns the user."""
    return click.style(fill(message, width=FW), fg="yellow")

def confirm(message):
    """Asks the user to confirm a potentially dangerous action.
    """
    return warn(message)

def error(message):
    return click.style(fill(message, width=FW), fg="red")

def success(message):
    return click.style(fill(message, width=FW), fg="green")
