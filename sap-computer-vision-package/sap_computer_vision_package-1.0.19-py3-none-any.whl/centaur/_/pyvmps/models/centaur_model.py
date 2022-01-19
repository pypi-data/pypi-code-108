from typing import Optional, List
from centaur._.pyvmps.models.base_model import Model
import psutil
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.cfg.config import EnvVarGoPyCommon

_logger = get_logger(__name__)


class CentaurModelMixin:
    """CentaurModel is intended to be subclassed by other model types"""

    def load_w_psutil(self: Model, target_cpus: List[int], trailing_cpus: List[int]) -> bool:
        _logger.debug("target_cpus=%s, trailing_cpus=%s", target_cpus, trailing_cpus)

        psutil.Process().cpu_affinity(cpus=target_cpus)
        load_res: bool = self.load()
        _logger.debug("successfully loaded model with cpu affinity settings=%s", psutil.Process().cpu_affinity())

        psutil.Process().cpu_affinity(cpus=trailing_cpus)
        _logger.debug("set model trailing cpu affinity with=%s", psutil.Process().cpu_affinity())

        return load_res
