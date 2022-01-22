"""CLI for Arduino API wrapper.
"""

import click
import sys

from . import ArduinoException, io, oled, rgb_lcd, shell


class ArduinoGroup(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except ArduinoException as e:
            sys.stderr.write(f"{e}\n")
            sys.exit(1)


@click.group(cls=ArduinoGroup)
def cli():
    # Load environment variables from .env if they exist
    import dotenv

    dotenv.load_dotenv()

    # Set up tracing, if desired
    import os

    try:
        from . import tracing
        tracing.set_default(os.getenv("TRACE"))
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)


@cli.command()
@click.option("-d", "--device", default="grove")
def test(device):
    import time

    if device == "grove":
        oled.clear()
        print_message = oled.print_message
    else:
        rgb_lcd.clear()
        print_message = rgb_lcd.print

    print_message("Testing...")
    time.sleep(0.5)

    count = 0

    while True:
        print_message(count)
        io.digital_write(4, count%2)

        time.sleep(0.1)
        count += 1


@cli.group()
def analog():
    """Commands to interact with analog pins."""
    pass


@analog.command("read")
@click.option("-c", "--continuous", is_flag=True)
@click.argument("pin", type=int)
def aread(pin, continuous):
    """Read a value from an analog pin."""

    if continuous:
        while True:
            print(io.analog_read(pin))
    else:
        print(io.analog_read(pin))


@analog.command("write")
@click.argument("pin", type=int)
@click.argument("duty", type=int)
def awrite(pin, duty):
    """Write a duty cycle to an analog pin."""

    io.analog_write(pin, duty)


@cli.group()
def digital():
    """Commands to interact with digital pins."""
    pass


@digital.command("read")
@click.option("-c", "--continuous", is_flag=True)
@click.argument("pin", type=int)
def dread(pin, continuous):
    """Read a value from a digital pin."""

    if continuous:
        while True:
            print(io.digital_read(pin))
    else:
        print(io.digital_read(pin))


@digital.command("write")
@click.argument("pin", type=int)
@click.argument("value", type=bool)
def dwrite(pin, value):
    """Write a bit cycle to a digital pin."""

    io.digital_write(pin, value)


@cli.group("lcd")
def lcd_group():
    """Commands to interact with the RGB LCD."""
    pass


@lcd_group.command("clear")
def lcd_clear():
    rgb_lcd.clear()


@lcd_group.command("colour")
@click.argument("red", type=int)
@click.argument("green", type=int)
@click.argument("blue", type=int)
def lcd_colour(red, green, blue):
    rgb_lcd.set_colour(red, green, blue)


@lcd_group.command("print")
@click.option("-r", "--row", type=int, default=0)
@click.option("-c", "--col", type=int, default=0)
@click.argument("message")
def lcd_print(row, col, message):
    rgb_lcd.print(row, col, message)


@cli.group("oled")
def oled_group():
    """Commands to print to the OLED display."""
    pass


@oled_group.command()
def clear():
    """Clear the OLED display."""

    oled.clear()


@oled_group.command("print")
@click.argument("message", type=str)
def oled_print(message):
    """Print a message to the OLED display."""

    oled.clear()
    oled.print_message(message)


@cli.command("shell")
def run_shell():
    """Directly interact with the remote device."""

    from . import tracing
    tracing.set_default('pretty')

    shell.GroveShell().cmdloop()
