from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class AlertType(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.severity = None
        self.message = None
        self.autoAchnowledge = None
        self.active = None
        self.timeoutActivation = None
        self.activationMessageEnabled = None
        self.timeoutDeactivation = None
        self.deactivationMessageEnabled = None
        self.deactivationMessage = None
        self.availabilityRelated = None
        self.operationRelated = None
        self.connectivitiyRelated = None
        self.criteria = None
        self.notificationReceivers = None
        self.notificationMessageLanguage = None
        self.notificationMessageRepeat = None
