from .base import BackendBase
from .bk_qiniu import Qiniu

backend_factory = {
    'qiniu': Qiniu
}