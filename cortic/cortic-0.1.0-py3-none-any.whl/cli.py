import click

@click.group()
def cli():
  pass

@click.command()
@click.option('--config')
def run(config):
  print(f'made it! {config}')