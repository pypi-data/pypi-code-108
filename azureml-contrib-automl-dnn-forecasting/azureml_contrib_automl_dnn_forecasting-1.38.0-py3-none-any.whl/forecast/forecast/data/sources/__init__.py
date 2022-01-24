"""Various datasets for evaluating algorithm performance."""

from forecast.data.sources.data_source import AbstractDataSource, DataSourceConfig, EncodingSpec  # noqa: F401
from forecast.data.sources.electricity import ElectricityDataSource  # noqa: F401
from forecast.data.sources.GEFCom14 import GEFCom14DataSource  # noqa: F401
from forecast.data.sources.github import GithubDataSource  # noqa: F401
from forecast.data.sources.m5 import M5DataSource  # noqa: F401
from forecast.data.sources.parts import PartsDataSource  # noqa: F401
