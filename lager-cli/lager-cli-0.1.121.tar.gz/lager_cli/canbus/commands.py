"""
    lager.canbus.commands

    Commands for canbus
"""
import math
import click
from ..context import get_default_gateway
from ..paramtypes import CanFrameType, CanFilterType, CanbusRange
from ..status import run_job_output

@click.group(name='canbus')
def canbus():
    """
        Lager CAN Bus commands
    """
    pass

@canbus.command('list')
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
def list_(ctx, gateway):
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.can_list(gateway)
    for interface in resp.json()['interfaces']:
        print(interface)


@canbus.command()
@click.pass_context
@click.argument('interfaces', type=CanbusRange())
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--bitrate', required=True, type=click.INT, help='bus bitrate e.g. 500000, 250000, etc')
def up(ctx, interfaces, gateway, bitrate):
    """
        Bring up the CAN Bus at the specified bitrate

        INTERFACES can be an integer, a dash-separated range of integers, or a comma-separated list
        of ranges or integers.

        Examples:

            \b
            lager canbus up 0      # Bring up canbus interface 0
            lager canbus up 0-1    # Bring up canbus interfaces 0 and 1
            lager canbus up 0,2    # Bring up canbus interfaces 0 and 2
            lager canbus up 0-1,3  # Bring up canbus interfaces 0, 1, and 3

        Use `lager canbus list` to view available INTERFACES.
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.can_up(gateway, bitrate, interfaces)
    print(resp.json()['message'])

@canbus.command()
@click.pass_context
@click.argument('interfaces', type=CanbusRange())
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
def down(ctx, interfaces, gateway):
    """
        Bring down the CAN Bus at the specified bitrate

        INTERFACES can be an integer, a dash-separated range of integers, or a comma-separated list
        of ranges or integers.

        Examples:

            \b
            lager canbus down 0      # Bring down canbus interface 0
            lager canbus down 0-1    # Bring down canbus interfaces 0 and 1
            lager canbus down 0,2    # Bring down canbus interfaces 0 and 2
            lager canbus down 0-1,3  # Bring down canbus interfaces 0, 1, and 3

        Use `lager canbus list` to view available INTERFACES.
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.can_down(gateway, interfaces)
    print(resp.json()['message'])


@canbus.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('interface', type=click.INT, required=True)
@click.argument('can_frames', required=True, nargs=-1, type=CanFrameType())
def send(ctx, gateway, interface, can_frames):
    """
        Send a frame on the specified CAN bus

        CAN_FRAME format:

        \b
        <can_id>#{R|data}
            for CAN 2.0 frames

        \b
        <can_id>##<flags>{data}
            for CAN FD frames

        \b
        <can_id>:
            can have 3 (SFF) or 8 (EFF) hex chars

        \b
        {data}:
            has 0..8 (0..64 CAN FD) ASCII hex-values (optionally separated by '.')

        \b
        <flags>:
            a single ASCII Hex value (0 .. F) which defines canfd_frame.flags

        \b
        CAN_FRAME Examples:
            5A1#11.2233.44556677.88 / 123#DEADBEEF / 5AA# / 123##1 / 213##311
            1F334455#1122334455667788 / 123#R for remote transmission request.
    """

    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.can_send(gateway, interface, can_frames)
    print(resp.json())


@canbus.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('interface', type=click.INT, required=True)
@click.argument('filters', required=False, nargs=-1, type=CanFilterType())
def dump(ctx, gateway, interface, filters):
    """
        Dump CAN bus traffic (use Ctrl-C to terminate)

        Zero or more filters can be specified in the format <can_id>:<can_mask>
        (matches when <received_can_id> & mask == can_id & mask)


        CAN IDs and masks are given and expected in hexadecimal values.  When can_id
        and  can_mask  are  both  8  digits, they are assumed to be 29 bit EFF. Without any
        filters all data frames are received ('0:0' default filter).

        Examples:

        \b
        lager canbus dump 0 92345678:DFFFFFFF
            (match only for extended CAN ID 12345678 on interface 0)

        \b
        lager canbus dump 0 123:7FF
            (matches CAN ID 123 - including EFF and RTR frames on interface 0)
    """
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    can_options = {
        'filters': [canfilter._asdict() for canfilter in filters],
    }
    can_session = session.can_dump(gateway, interface, can_options).json()
    job_id = can_session['test_run']['id']

    region = ctx.obj.session.region(gateway)
    connection_params = ctx.obj.websocket_connection_params(socktype='job', job_id=job_id, region=region)
    run_job_output(connection_params, None, False, None, math.inf, math.inf, None, ctx.obj.debug)
