from typing import Dict, Tuple

from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.base_model import BatchedModel
from centaur._.pyvmps.models.python.model import PythonModel
from centaur._.pyvmps.models.centaur_model import CentaurModelMixin
from centaur._.pyvmps.models.python.utils import batch_predict

_logger = get_logger(__name__)


class PymodelPyvmp(PythonModel, BatchedModel, CentaurModelMixin):
    """PymodelPyvmp."""

    def _single_predict(self, single_req_payload: Dict[str, Dict]) -> Tuple[Dict, Dict]:
        return batch_predict(single_req_payload, self.verb_funcs)

    def _batch_predict(self, batch_req_payload: Dict[str, Dict]):
        return batch_predict(batch_req_payload, self.verb_funcs)
