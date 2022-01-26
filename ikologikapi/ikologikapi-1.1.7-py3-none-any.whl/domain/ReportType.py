from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class ReportType(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.type = None
        self.outputType = None
        self.name = None
        self.title = None
        self.fileName = None
        self.contentType = None
        self.comment = None
        self.scheduleActive = None
        self.schedule = None
        self.dateEditable = None
        self.titleEditable = None
        self.filenameEditable = None
        self.reviewEnabled = None
        self.reviewReceivers = None
        self.reviewReceiversSendRequired = None
        self.notificationReceivers = None
        self.notificationReceiversSendRequired = None
