import click
import pkgutil
import importlib
import os
import sys
import time

def receiver_options(function):
    receivers_module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'receivers')
    receiver_names = [module_info.name for module_info in pkgutil.iter_modules([receivers_module_path])]
    for receiver in receiver_names:
        function = click.option(f'--{receiver}', default=None, help=f'{receiver} sources to check, comma-separated without spaces')(function)
    return function

@click.command()
@receiver_options
@click.option('--timeout', required=True, default=None, help='number of seconds to keep waiting for a message')
@click.option('--num-checks', required=False, default=None, help='number of times to check for a message')
@click.argument('pattern')
def get_cli(pattern, **kwargs):
    # Make a matrix of Rito receiver modules to the list of sources they should receive from
    message_matrix = {}
    
    timeout = None
    interval = 1
    num_checks = None
    for receiver_arg, source_arg in kwargs.items():
        if receiver_arg == 'timeout':
            timeout = int(source_arg)
            continue
        if receiver_arg == 'num_checks':
            num_checks = int(source_arg)
            continue
        if source_arg == None:
            continue
        receiver_module = importlib.import_module(f'rito.receivers.{receiver_arg}')
        sources=source_arg.split(",")
        message_matrix[receiver_module] = sources

    if num_checks != None:
        interval = timeout / num_checks

    if len(message_matrix) == 0:
        print("Your rito-get command wouldn't receive any messages. Check your arguments")
        exit(1)
    
    # Manage the timeout/retry loop for receivers
    t = 0
    while t < timeout:
        for module, sources in message_matrix.items():
            if t % module.check_interval == 0:
                for source in sources:
                    m = module.get_message(source, pattern)
                    if m != None and len(m) > 0:
                        print(m)
                        sys.exit(0)
        t += interval
        time.sleep(interval)
    sys.stderr.write(f"rito-get timeout after {timeout}.{os.linesep}")
    sys.exit(1)