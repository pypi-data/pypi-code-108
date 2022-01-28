from cef_logger import Event


# Creating Base event with Extension and custom fields

class BaseEventForTest(Event):
    Version = 1
    DeviceProduct = 'MyProduct'
    DeviceVersion = '1.0'
    DeviceVendor = 'MyCompany'
    DeviceEventClassID = 'base'
    Name = 'base'
    Severity = 1


# Creating New event with Extension and customs fields

class NewEventForTest(BaseEventForTest):
    src = '192.168.0.1'
    dst = 2
    shost = 3
    msg = 4
    spid = 5
    custom_field = 'custom_example'


# Creating Base event with error
class BaseEventWithError(Event):
    Version = 'error data'
    DeviceProduct = 'MyProduct'
    DeviceVersion = '1.0'
    DeviceVendor = 'MyCompany'
    DeviceEventClassID = 'base'
    Name = 'base'
    Severity = 1
