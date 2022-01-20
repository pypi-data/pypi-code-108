from overrides import overrides
from torch.optim.lr_scheduler import _LRScheduler, ReduceLROnPlateau as BaseModel

from ..callbacks import CallbackName
from ..nwmodule import NWModule
from ..logger import logger

class ReduceLROnPlateau(_LRScheduler):
    def __init__(self, model: NWModule, metric: str, factor: float, patience: int, **kwargs):
        self.metric = metric
        if factor > 1:
            logger.debug(f"Factor is greater than one: {factor}. Setting to 1/factor={1 / factor}")
            factor = 1 / factor
        self.base_model = BaseModel(model.getOptimizer(), factor=factor, patience=patience, **kwargs)
        self.model = model
        # TODO: Make a scheduler class.
        self.storedArgs = {}

    @overrides
    def step(self, epoch=None):
        assert not self.model is None
        history = self.model.trainHistory[-1]
        key = "Validation" if "Validation" in history and not history["Validation"] is None else "Train"
        metric = history[key][CallbackName(self.metric)]
        self.base_model.step(metric)

    @overrides
    def state_dict(self):
        state_dict = self.base_model.state_dict()
        state_dict["metric"] = self.metric
        return {**state_dict, "metric": self.metric}

    @overrides
    def load_state_dict(self, state_dict):
        self.base_model.load_state_dict(state_dict)

    def __str__(self):
        return f"ReduceLROnPlateau. Metric: {self.metric}. Patience: {self.patience}. Factor: {self.factor}."

    def __getattr__(self, name):
        return {
            "patience" : self.base_model.patience,
            "factor" : self.base_model.factor,
            "optimizer" : self.base_model.optimizer,
            "num_bad_epochs" : self.base_model.num_bad_epochs
        }[name]
