"""
Common commands
"""
import click

from montecarlodata.tools import convert_uuid_callback

DISAMBIGUATE_DC_OPTIONS = [
    click.option('--collector-id', 'dc_id', required=False, type=click.UUID, callback=convert_uuid_callback,
                 help='ID for the data collector. To disambiguate accounts with multiple collectors.'),
]
