from ml.fml40.roles.dts.sites.mill.mill import Mill


class Papermill(Mill):
    def __init__(self, namespace="fml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)
