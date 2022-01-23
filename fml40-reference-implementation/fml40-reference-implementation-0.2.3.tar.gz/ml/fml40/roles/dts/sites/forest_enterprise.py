from ml.ml40.roles.dts.sites.site import Site


class ForestEnterprise(Site):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
