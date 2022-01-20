from arthurai.core.bias.threshold_mitigation import ThresholdMitigation
from arthurai.core.bias.bias_metrics import BiasMetrics


class ArthurBiasWrapper(object):
    """
    This is a wrapper class for all bias-related functionality, including metrics
    and mitigation. This allows users to access bias functionality directly from the
    ArthurModel object: `arthur_model.bias.metrics`, for example. 
    """
    def __init__(self, arthur_model):

        self.model = arthur_model
        self.metrics = BiasMetrics(self.model)
        self.mitigation_threshold = ThresholdMitigation(self.model)
