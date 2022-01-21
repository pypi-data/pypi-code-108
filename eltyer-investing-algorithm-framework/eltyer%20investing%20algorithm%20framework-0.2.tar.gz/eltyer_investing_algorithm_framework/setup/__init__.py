from investing_algorithm_framework import App

from eltyer_investing_algorithm_framework.configuration import constants
from eltyer_investing_algorithm_framework.initializer import EltyerInitializer
from eltyer_investing_algorithm_framework.order_executor import \
    EltyerOrderExecutor
from eltyer_investing_algorithm_framework.portfolio_manager import \
    EltyerPortfolioManager


def create_app(resources_directory, config={}, trading_bot_api_key=None):
    app = App(
        resources_directory=resources_directory,
        config=config
    )

    if trading_bot_api_key is not None:
        app.config[constants.ELTYER_API_KEY] = trading_bot_api_key

    app.add_initializer(EltyerInitializer)
    app.add_order_executor(EltyerOrderExecutor)
    app.add_portfolio_manager(EltyerPortfolioManager)
    return app
