from ml.ml40.roles.dts.handheld_devices.handheld_device import HandheldDevice


class Chainsaw(HandheldDevice):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
