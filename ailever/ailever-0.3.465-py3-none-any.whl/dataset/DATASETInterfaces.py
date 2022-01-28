from .from_ailever import Integrated_Loader
from .from_statsmodels import Statsmodels_API
from .from_sklearn import Sklearn_API
from .from_ailever import Ailever_API
from .uci_machine_learning_repository import UCI_MLR

AILAPI = Ailever_API

Loader = Integrated_Loader()
SMAPI = Statsmodels_API()
SKAPI = Sklearn_API()
UCI = UCI_MLR()
