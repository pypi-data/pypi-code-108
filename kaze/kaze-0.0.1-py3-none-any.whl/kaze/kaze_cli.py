import click


@click.command()
@click.option("--source", "-s", default="", help="Source file")
@click.option("--output", "-o", default="", help="Output file")
@click.option("--format", "-f", default="", help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode")
def get(source, output, format, verbose):
    print(f"getting from {source} to {output}")
