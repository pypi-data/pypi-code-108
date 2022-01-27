from collections import OrderedDict


class CustomPropertyRepository:
    def __init__(self):
        self.custom_properties = OrderedDict()
        self.custom_property_added_handlers = []

    def add_custom_property(self, custom_property):
        if not custom_property.name:
            return

        self.custom_properties[custom_property.name] = custom_property
        self.raise_custom_property_added_event(custom_property)

    def add_custom_property_if_not_exists(self, custom_property):
        if not custom_property.name or custom_property.name in self.custom_properties:
            return

        self.add_custom_property(custom_property)

    def get_custom_property(self, name):
        return self.custom_properties.get(name, None)

    def get_all_custom_properties(self):
        return self.custom_properties

    def register_custom_property_added_handler(self, handler):
        self.custom_property_added_handlers.append(handler)

    def raise_custom_property_added_event(self, custom_property):
        for handler in self.custom_property_added_handlers:
            handler(custom_property)
