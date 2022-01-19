import numpy as np


class BacktestDataHandler(object):
    """
    """

    def __init__(
        self,
        universe,
        data_sources=None
    ):
        self.universe = universe
        self.data_sources = data_sources

    def get_asset_latest_bid_price(self, dt, asset_symbol, complain=False):
        """
        """
        # TODO: Check for asset in Universe
        bid = np.NaN
        for ds in self.data_sources:
            bid = ds.get_bid(dt, asset_symbol, complain)
            if not np.isnan(bid):
                return bid
        return bid

    def get_asset_latest_ask_price(self, dt, asset_symbol, complain=False):
        """
        """
        # TODO: Check for asset in Universe
        ask = np.NaN
        for ds in self.data_sources:
            ask = ds.get_ask(dt, asset_symbol, complain)
            if not np.isnan(ask):
                return ask
        return ask

    def get_asset_latest_bid_ask_price(self, dt, asset_symbol, complain=False):
        """
        :param complain: Raise an exception if there is data missing
        """
        # TODO: For the moment this is sufficient for OHLCV
        # data, which only usually provides mid prices
        # This will need to be revisited when handling intraday
        # bid/ask time series.
        # It has been added as an optimisation mechanism for
        # interday backtests.
        bid = self.get_asset_latest_bid_price(dt, asset_symbol, complain)
        return (bid, bid)

    def get_asset_latest_mid_price(self, dt, asset_symbol, complain):
        """
        """
        bid_ask = self.get_asset_latest_bid_ask_price(dt, asset_symbol, complain)
        try:
            mid = (bid_ask[0] + bid_ask[1]) / 2.0
        except Exception:
            # TODO: Log this
            mid = np.NaN
        return mid

    def get_assets_historical_range_close_price(
        self, start_dt, end_dt, asset_symbols, adjusted=False
    ):
        """
        """
        prices_df = None
        for ds in self.data_sources:
            try:
                prices_df = ds.get_assets_historical_closes(
                    start_dt, end_dt, asset_symbols, adjusted=adjusted
                )
                if prices_df is not None:
                    return prices_df
            except Exception:
                raise
        return prices_df
