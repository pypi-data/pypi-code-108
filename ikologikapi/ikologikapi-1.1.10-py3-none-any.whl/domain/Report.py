from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class Report(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.type = None
        self.lastProcessing = None
        self.nextProcessing = None
        self.lockedUntil = None
        self.reportType = None
        self.date = None
        self.title = None
        self.fileName = None
        self.contentType = None
        self.comment = None
        self.sendReviewNotifications = None
        self.sendNotifications = None
        self.user = None
        self.status = None
        self.fields = None

