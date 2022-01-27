from ikologikapi.domain.AbstractIkologikObject import AbstractIkologikObject


class TagAlertType(AbstractIkologikObject):

    def __init__(self):
        super().__init__()
        self.meter = None
        self.value = None
        self.type = None
        self.severity = None
        self.message = None
        self.autoAcknowledge = None
        self.active = None
        self.activationMessageEnabled = None
        self.activationMessage = None
        self.deactivationMessageEnabled = None
        self.deactivationMessage = None
        self.availabilityRelated = None
        self.operationRelated = None
        self.connectivityRelated = None
        self.notificationReceivers = None
