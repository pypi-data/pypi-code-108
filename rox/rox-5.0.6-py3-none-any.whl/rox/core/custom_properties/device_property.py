from rox.core.custom_properties.custom_property import CustomProperty


class DeviceProperty(CustomProperty):
    def __init__(self, name, type, value):
        super(DeviceProperty, self).__init__('rox.%s' % name, type, value)
