"""
    lager.gpio.commands

    Commands for manipulating gateway GPIO lines
"""
import click
from ..context import get_default_gateway

@click.group()
def gpio():
    """
        Lager gpio commands
    """
    pass

_GPIO_CHOICES = click.IntRange(0, 14)
_LEVEL_CHOICES = click.Choice(('LOW', 'HIGH', 'ON', 'OFF'), case_sensitive=False)
_BUS_CHOICES = click.Choice(['5V', '3V3'], case_sensitive=False)

@gpio.command(name='set')
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('gpio_', metavar='GPIO', type=_GPIO_CHOICES)
@click.argument('type_', type=click.Choice(('IN', 'OUT', 'ALT0', 'ALT1', 'ALT2', 'ALT3', 'ALT4', 'ALT5'), case_sensitive=False))
@click.option('--pull', type=click.Choice(('UP', 'DOWN', 'OFF'), case_sensitive=False), default='OFF', show_default=True, help='Sets or clears the internal GPIO pull-up/down resistor.')
@click.pass_context
def set_(ctx, gateway, gpio_, type_, pull):
    """
        Sets pin GPIO mode (input/output)

        If type is IN, --pull controls the internal GPIO pull-up/down resistor.
        Otherwise it has no effect.

        GPIO can be 0-14
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    if type_ != 'IN' and pull != 'OFF':
        click.echo(f'GPIO pin {gpio_} set as output, ignoring --pull', err=True)

    ctx.obj.session.gpio_set(gateway, gpio_, type_, pull)


@gpio.command(name='input')
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('gpio_', metavar='GPIO', type=_GPIO_CHOICES)
@click.pass_context
def input_(ctx, gateway, gpio_):
    """
        Returns GPIO level (0 for low, 1 for high)

        GPIO can be 0-14
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)
    result = ctx.obj.session.gpio_input(gateway, gpio_)
    click.echo(result.json()['level'])


@gpio.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('gpio_', metavar='GPIO', type=_GPIO_CHOICES)
@click.argument('level', type=_LEVEL_CHOICES)
@click.pass_context
def output(ctx, gateway, gpio_, level):
    """
        Sets GPIO level.

        GPIO can be 0-14
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)
    ctx.obj.session.gpio_output(gateway, gpio_, level)


@gpio.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('gpio_', metavar='GPIO', type=_GPIO_CHOICES)
@click.option('--pulse-length', type=click.IntRange(1, 100), help='Pulse length in microseconds (1-100)', required=True)
@click.option('--level', type=_LEVEL_CHOICES, help='Pulse level', required=True)
@click.pass_context
def trigger(ctx, gateway, gpio_, pulse_length, level):
    """
        Send a trigger pulse to GPIO.
        The GPIO is set to level for pulse-length microseconds and then reset to not level.

        GPIO can be 0-14
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)
    ctx.obj.session.gpio_trigger(gateway, gpio_, pulse_length, level)


@gpio.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('bus_', metavar='POWER_BUS', type=_BUS_CHOICES)
@click.argument('level', type=_LEVEL_CHOICES)
@click.pass_context
def power(ctx, gateway, bus_, level):
    """
        Sets level on power bus enable lines

    """
    if gateway is None:
        gateway = get_default_gateway(ctx)
    ctx.obj.session.gpio_power(gateway, bus_, level)

