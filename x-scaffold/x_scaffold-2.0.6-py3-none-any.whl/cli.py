import sys
import click
import logging

from click.decorators import help_option

from x_scaffold import engine
from x_scaffold.context import ScaffoldContext
from x_scaffold.runtime import ScaffoldConsoleRuntime


class AddColorFormatter(logging.Formatter):
    def format(self, record):
        msg = super(AddColorFormatter, self).format(record)
        # Green/Cyan/Yellow/Red/Redder based on log level:
        color = (
            "\033[1;"
            + ("32m", "36m", "33m", "31m", "41m")[
                min(4, int(4 * record.levelno / logging.FATAL))
            ]
        )
        return color + record.levelname + "\033[1;0m: " + msg


@click.command('apply', help='Apply a scaffold')
@click.argument('package')
@click.option('-n', '--name', default='xscaffold', help='The name of the scaffold to apply')
@click.option('-t', '--target', default='.', help='Target directory to apply scaffold')
@click.option('-p', '--parameter', multiple=True, help='Parameters to set in the context')
def apply_cli(package, name, target, parameter):
    context = ScaffoldContext({
        '__target': target
    })
    p: str
    for p in parameter:
        eq_idx = p.index('=')
        parameter_name = p[0:eq_idx]
        parameter_value = p[eq_idx+1:]
        context[parameter_name] = parameter_value
    engine.run(context, {
        'package': package,
        'name': name
    }, ScaffoldConsoleRuntime())


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--log-level', default='info', help='The log level to output')
def cli(log_level):
    stdout_hdlr = logging.StreamHandler(stream=sys.stdout)
    stdout_hdlr.setFormatter(AddColorFormatter())

    logging.root.handlers.clear()

    loglevel_str = log_level.upper()
    loglevel = getattr(logging, loglevel_str)

    stdout_hdlr.setLevel(loglevel)
    logging.root.setLevel(loglevel)
    logging.root.addHandler(stdout_hdlr)
    pass

cli.add_command(apply_cli)

if __name__ == '__main__':
    cli()
