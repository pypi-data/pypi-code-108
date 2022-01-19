from typing import Dict, Tuple


class Model:
    """Model is the base class that represents a model. All models should subclass this base class"""

    def load(self) -> bool:
        self.ready = True
        return self.ready

    def predict(self, payload: Dict, **kwargs) -> Dict:  # pylint:disable=no-self-use
        pass


class BatchedModel(Model):
    """BatchedModel is the abstract class for batching in pyvmp. All models returned in pyvmp should implement the abstract methods"""

    def _single_predict(self, batch_dict: Dict) -> Tuple[Dict, Dict]:
        pass

    def _batch_predict(self, batch_dict: Dict) -> Tuple[Dict, Dict]:
        pass
