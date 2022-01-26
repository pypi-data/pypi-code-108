from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class Dashboard(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.name = None
        self.type = None
        self.active = True
        self.parameters = []
        self.mapping = DataImportTypeMapping()


class DataImportTypeMapping(object):

    def __init__(self):
        self.tags = []


class DataImportMappingTag(object):
    def __init__(self):
        self.sourceId
        self.sourceName
        self.sourceDataType
        self.sourceDescription
        self.tag
