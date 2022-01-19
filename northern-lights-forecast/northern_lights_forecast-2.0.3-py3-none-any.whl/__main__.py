"""Command-line interface."""
import click

import northern_lights_forecast.img as img
import northern_lights_forecast.northern_lights as nl
from northern_lights_forecast.__init__ import __version__


@click.command()
@click.version_option(version=__version__)
@click.option(
    "-l",
    "--location",
    type=str,
    default="Tromsø",
    show_default=True,
    help="Which magnetometer to use. "
    + "Run with '--locations' option to list all available locations.",
)
@click.option(
    "--locations/--no-locations",
    type=bool,
    default=False,
    show_default=True,
    help="List out available magnetometer locations.",
)
@click.option(
    "--test/--no-test",
    type=bool,
    default=False,
    show_default=True,
    help="Test sending message to telegram.",
)
def main(location: str, locations: bool, test: bool) -> None:
    """Northern Lights Forecast."""
    if test:
        nl.telegram_test()
        return
    if locations:
        for loc in img.__PLACE__.keys():
            print(loc)
        return
    if location not in img.__PLACE__.keys():
        raise ValueError(
            f"'{location}' is not a valid location. Run with option "
            + "'--locations' to see available locations."
        )
    nl.nlf(location)


if __name__ == "__main__":
    main(prog_name="northern-lights-forecast")  # pragma: no cover
