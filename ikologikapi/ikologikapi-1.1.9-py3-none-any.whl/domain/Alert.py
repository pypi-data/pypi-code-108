from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class Alert(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.alertType = None
        self.startDate = None
        self.endDate = None
        self.active = None
        self.severity = None
        self.message = None
        self.availablilityRelated = None
        self.operationRelated = None
        self.connectivityRelated = None
        self.acknowledgeDate = None
        self.meters = None
        self.nrOfComments = None
