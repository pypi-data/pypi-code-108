# https://github.com/yujitach/MenuMeters/blob/main/hardware_reader/applesilicon_hardware_reader.m

import objc
from Foundation import NSBundle
from CoreFoundation import *

IOKit = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')
objc.loadBundleFunctions(IOKit, globals(), [
    ('IOHIDEventSystemClientCreate', b'@@'),
    ('IOHIDEventSystemClientSetMatching', b'v@@'),
    ('IOHIDEventSystemClientCopyServices', b'@@'),
    ('IOHIDServiceClientCopyProperty', b'@@@'),
    ('IOHIDServiceClientCopyEvent', b'@@III'),
    ('IOHIDEventGetFloatValue', b'd@I'),
])


def get_client_services():
    defaultAllocator = CFAllocatorGetDefault()
    eventSystem = IOHIDEventSystemClientCreate(defaultAllocator)
    thermalSensors = {'PrimaryUsagePage': 0xff00, 'PrimaryUsage': 5}
    IOHIDEventSystemClientSetMatching(eventSystem, thermalSensors)
    mathingServices = IOHIDEventSystemClientCopyServices(eventSystem)
    return mathingServices


def get_sensor_names():
    services = get_client_services()

    for service in services:
        name = IOHIDServiceClientCopyProperty(service, 'Product')
        if name:
            yield name


def get_temperature(sensor_name_contains):
    services = get_client_services()

    for service in services:
        name = IOHIDServiceClientCopyProperty(service, 'Product')
        if sensor_name_contains.lower() not in name.lower():
            continue
        kIOHIDEventTypeTemperature = 15
        event = IOHIDServiceClientCopyEvent(service, kIOHIDEventTypeTemperature, 0, 0)
        if event:
            tempFieldBase = kIOHIDEventTypeTemperature << 16
            temp = IOHIDEventGetFloatValue(event, tempFieldBase)
            yield temp


def get_cpu_temperature():
    # sensors = [sensor for sensor in list(get_sensor_names()) if 'soc' in sensor.lower()]
    temps = list(get_temperature('SOC'))
    return max(temps)


def get_temperature_subprocess(queue):
    queue.put(get_cpu_temperature())


if __name__ == '__main__':
    print(get_cpu_temperature())
