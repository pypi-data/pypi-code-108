
import click


@click.command()
@click.argument("arg")
def cli(arg):
    print(arg)


if __name__ == "__main__":
    cli()

