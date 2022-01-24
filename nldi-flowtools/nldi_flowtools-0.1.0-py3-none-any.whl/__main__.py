"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Nldi Flowtools."""


if __name__ == "__main__":
    main(prog_name="nldi-flowtools")  # pragma: no cover
