from ml.fml40.roles.dts.machines.forest_machine import ForestMachine


class Harvester(ForestMachine):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
