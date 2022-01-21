import click
from mt_html.mt_code import html_dump
from mt_html.env_creator import create_env_file

@click.group(help="""This simple tool logins to a Mikrotik and creats an HTML dump""")
def cli():
    pass

@cli.command()
def generate_env():
    return create_env_file()

@cli.command()
@click.option(
    '--firewall', '-f', help='Firewall you wish to create an HTML dump for',
    required=True,
    type=str,
)
def dump(firewall):
    return html_dump(firewall)


