from ml.ml40.roles.hmis.hmi import HMI


class Dashboard(HMI):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(Dashboard, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
