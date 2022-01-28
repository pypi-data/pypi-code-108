from .assets import Asset
from .stock_market import market_information, market_monitoring
from .screener import Screener
from .portfolio_optimization import PortfolioManagement
from .fmlops_models import Forecaster
from .fmlops_loader_system import Loader, ILoader, PLoader, Preprocessor
from .investment_management import IMQuery
from . import sectors

prllz_loader = PLoader.prllz_loader
parallelize = PLoader.parallelize


def Management(system):
    return locals()[system]
