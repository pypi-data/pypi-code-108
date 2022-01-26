from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class Batch(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.batchType = None
        self.code = None
        self.description = None
        self.status = None
        self.startDate = None
        self.endDate = None
        self.active = None
        self.fields = None


class BatchField(object):

    def __init__(self):
        self.stringValue = None
        self.booleanValue = None
        self.numberValue = None
        self.dateValue = None
        self.timeValue = None
        self.dateTimeValue = None
        self.LookupListValue = None
