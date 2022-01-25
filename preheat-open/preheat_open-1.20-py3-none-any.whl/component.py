class Component(object):
    """Defines a Component in the PreHEAT sense"""

    def __init__(self, component_data):
        # Identifier of the component
        self.cid = component_data.pop("cid", None)
        self.id = component_data.pop("id", None)

        # Name of the component
        self.name = component_data.pop("name", str(self.id))

        # Tag (e.g. BACNET/source name)
        self.tag = component_data.pop("tag", None)

        # Data for the component (PreHEAT_API.Data)
        self.data = None

        # Factor to divide by to obtain a 'standard' unit
        self.std_unit_devisor = component_data.pop("stdUnitDivisor", 1)

        # Standard unit for this type of component
        self.std_unit = component_data.pop("stdUnit", "")

    def __repr__(self):
        return "{0}({1}, {2})".format(type(self).__name__, self.name, self.tag)
