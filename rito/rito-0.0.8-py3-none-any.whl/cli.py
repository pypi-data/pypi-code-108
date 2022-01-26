import click
import pkgutil
import importlib
import os

def sender_options(function):
    senders_module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'senders')
    sender_names = [module_info.name for module_info in pkgutil.iter_modules([senders_module_path])]
    for sender in sender_names:
        function = click.option(f'--{sender}', default=None, help=f'{sender} recipients to message, comma-separated without spaces')(function)
    return function

@click.command()
@sender_options
@click.argument('message')
def cli(message, **kwargs):
    # Make a matrix of Rito modules to the list of recipients they should send to
    message_matrix = {}
    
    for sender_arg, recipients_arg in kwargs.items():
        if recipients_arg == None:
            continue
        sender_module = importlib.import_module(f'rito.senders.{sender_arg}')
        recipients=recipients_arg.split(",")
        message_matrix[sender_module] = recipients

    if len(message_matrix) == 0:
        print("Your rito command wouldn't send any messages. Check your arguments")
        exit(1)
    
    for module, recipients in message_matrix.items():
        for recipient in recipients:
            module.send_message(recipient, message)