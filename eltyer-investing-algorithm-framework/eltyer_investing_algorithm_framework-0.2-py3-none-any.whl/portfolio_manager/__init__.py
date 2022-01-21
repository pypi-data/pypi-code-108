import logging

from investing_algorithm_framework import SQLLitePortfolioManager
from eltyer_investing_algorithm_framework.configuration import constants
from eltyer import Client

logger = logging.getLogger(__name__)


class EltyerPortfolioManager(SQLLitePortfolioManager):
    identifier = "ELTYER"
    market = "ELTYER"

    def initialize(self, algorithm_context):
        client: Client = algorithm_context.config[constants.ELTYER_CLIENT]
        client.start()
        logger.info(client.get_environment())
        portfolio = client.get_portfolio()
        self.market = portfolio.broker

        self.trading_symbol = portfolio.trading_symbol
        algorithm_context.config\
            .set("TRADING_SYMBOL", portfolio.trading_symbol)
        super(EltyerPortfolioManager, self).initialize(algorithm_context)

    def get_unallocated_synced(self, algorithm_context):
        client: Client = algorithm_context.config.get(constants.ELTYER_CLIENT)
        return client.get_portfolio().unallocated

    def get_positions_synced(self, algorithm_context):
        client: Client = algorithm_context.config.get(constants.ELTYER_CLIENT)
        positions = client.get_positions(json=True)
        return positions
