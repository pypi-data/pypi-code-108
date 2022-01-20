from .integrated_loader import Loader
from .integrated_loader import IntegratedLoader
from .parallelizer import ParallelizationLoader
from .preprocessor import Preprocessor

ILoader = IntegratedLoader()
PLoader = ParallelizationLoader()
parallelize = PLoader.parallelize

