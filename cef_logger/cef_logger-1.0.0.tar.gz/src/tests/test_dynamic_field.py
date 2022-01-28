from datetime import datetime
from time import sleep

from cef_logger import Fields


# Create a dynamic field
class GetCurrentUnixTimestamp:
    # Generating timestamp on render log message
    def __repr__(self):
        return f'{int(datetime.utcnow().timestamp())}'


def test_dynamic_field():
    fields = Fields(

        **{
            'Version': 1, 'DeviceProduct': 'MyProduct',
            'DeviceVersion': '1.0', 'DeviceVendor': 'MyCompany',
            'DeviceEventClassID': 'base', 'Name': 'base', 'Severity': 1,
            'end': GetCurrentUnixTimestamp()
        },
    )
    time_1 = fields.render()
    sleep(1)
    time_2 = fields.render()
    assert time_1 != time_2
