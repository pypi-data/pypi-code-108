from ikologikapi.domain.AbstractIkologikInstallationsObject import AbstractIkologikInstallationsObject


class Tag(AbstractIkologikInstallationsObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)
        self.type = None
        self.name = None
        self.identification = None
        self.description = None
        self.group = None
        self.importStatus = None
        self.unit = None
        self.valueType = None
        self.valueTimeUnit = None
        self.decimalPrecision = None
        self.color = None
        self.visible = None
        self.visibleTroubleshooting = None
        self.gridAlignmentValue = None
        self.gridAlignmentUnit = None
        self.transformationActive = None
        self.transformationMultiplier = None
        self.transformationAdd = None
        self.transformationRounding = None
        self.minLimit = None
        self.lowLowLimit = None
        self.lowLimit = None
        self.highLimit = None
        self.maxLimit = None
        self.highHighLimit = None
        self.maxLimit = None
        self.medianActive = None
        self.epsilon = None
        self.medianActive = None
        self.medianSampleSize = None
        self.trendActive = None
        self.trendSampleSize = None
        self.epsilon = None
        self.dataImportStatus = None
        self.lastDataImportStatusUpdate = None
