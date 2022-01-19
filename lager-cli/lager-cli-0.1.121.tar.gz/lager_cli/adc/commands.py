"""
    lager.adc.commands

    ADC (analog/digital converter) commands
"""

import click
from ..context import get_default_gateway
from ..paramtypes import ADCChannelType

@click.group(name='adc')
def adc():
    """
        ADC (analog/digital converter) commands
    """
    pass

_RESULT_COUNT = click.Choice(('1', '4', '8', '12', '16'))
_AVERAGE_COUNT = click.Choice(('none', '4', '8', '16', '32'))
_OUTPUT_TYPE = click.Choice(('raw', 'mV'), case_sensitive=False)

def _get_default_average_count():
    # TODO: implement
    return 0

def _get_default_result_count():
    # TODO: implement
    return 1

def _get_default_output():
    # TODO: implement
    return 'raw'

@adc.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--average-count', required=False, type=_AVERAGE_COUNT, help='Averaging count')
@click.option('--output', type=_OUTPUT_TYPE, required=False, help='Output mode')
@click.argument('CHANNEL', type=ADCChannelType(), required=False)
def read(ctx, gateway, average_count, output, channel):
    """
        Read the analog-digital convertor on the gateway
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    if average_count is None:
        average_count = _get_default_average_count()
    else:
        if average_count.lower() == 'none':
            average_count = None
        else:
            average_count = int(average_count, 10)

    if output is None:
        output = _get_default_output()
    else:
        output = output.lower()

    session = ctx.obj.session
    resp = session.read_adc(gateway, channel, average_count, output)

    print(resp.json())


@adc.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
def settings(ctx, gateway):
    """
        (Currently not implemented) Set defaults for average-count, result-count, and output
    """
    pass
