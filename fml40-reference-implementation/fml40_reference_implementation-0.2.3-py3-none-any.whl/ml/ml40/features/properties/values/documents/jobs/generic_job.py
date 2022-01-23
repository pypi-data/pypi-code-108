from ml.ml40.features.properties.values.documents.jobs.job import Job


class GenericJob(Job):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__content = None
        self.__json_out = dict()

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        self.__content = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.content is not None:
            self.__json_out["content"] = self.content

        return self.__json_out
