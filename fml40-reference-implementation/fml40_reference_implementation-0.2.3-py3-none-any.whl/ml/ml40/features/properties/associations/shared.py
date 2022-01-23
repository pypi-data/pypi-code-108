from ml.ml40.features.properties.associations.association import Association


class Shared(Association):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__targets = []
        self.__targets = dict()
        self.__json_out = dict()

    @property
    def targets(self):
        return self.__targets

    @targets.setter
    def targets(self, value):
        self.__targets = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.targets:
            self.__json_out["targets"] = []
            for key in self.__targets.keys():
                self.__json_out["targets"].append(self.targets[key].entry.refresh_sub_thing_repo_entry())
        return self.__json_out
