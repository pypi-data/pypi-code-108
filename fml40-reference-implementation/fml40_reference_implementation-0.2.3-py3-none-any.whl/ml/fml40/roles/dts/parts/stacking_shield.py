from ml.ml40.roles.dts.parts.part import Part


class StackingShield(Part):
    """roles for stacking shield"""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
