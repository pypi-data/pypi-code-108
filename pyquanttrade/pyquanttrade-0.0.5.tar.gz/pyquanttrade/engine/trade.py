# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"
import logging


class Trade:
    def __init__(
        self,
        order_type,
        ticker,
        day,
        price,
        num_actions=1,
        stop_loss=1,
        stop_loss_trailing=False,
        commission=0,
        slippage=0,
    ):

        self.type = order_type
        self.ticker = ticker
        self.open_day = day
        self.close_day = "None"
        self.close_price = "None"
        self.state = "OPENED"
        self.open_price = price
        self.init_capital = price * num_actions
        self.num_actions = num_actions
        self.profit = 0
        self.stop_loss = stop_loss
        self.up_price = self.open_price
        self.stop_loss_trailing = stop_loss_trailing
        self.commission = commission
        self.slippage = slippage
        self.num_days = 0

    def close(self, day, price):
        self.close_day = day
        if self.type == "long":
            self.close_price = max(price, (1 - self.stop_loss) * self.up_price)
            self.profit = (
                self.num_actions
                * (self.close_price - self.open_price - self.commission)
                - self.slippage
            )
        else:
            self.close_price = min(price, (1 + self.stop_loss) * self.up_price)
            self.profit = (
                self.num_actions
                * (self.open_price - self.close_price - self.commission)
                - self.slippage
            )

        self.state = "CLOSED"


class TradeList:
    def __init__(self, level):
        self.trade_index = float(0)
        self.trades_opened = {}
        self.trades_closed = {}
        logging.basicConfig(level=level)
        self.logger = logging.getLogger(__name__)

    def any_open_trade(self):
        return bool(self.trades_opened)

    def open_trade(
        self,
        ticker,
        order_type,
        day,
        price,
        num_actions=1,
        stop_loss=1,
        stop_loss_trailing=False,
        commission=0,
        slippage=0,
    ):
        self.trade_index += 1
        trade = Trade(
            order_type,
            ticker,
            day,
            price,
            num_actions,
            stop_loss,
            stop_loss_trailing,
            commission,
            slippage,
        )
        self.trades_opened[self.trade_index] = trade

    def close_open_trades(self, ticker, order_type, day, price):
        count = 0
        money = 0
        for key in list(self.trades_opened.keys()):
            v = self.trades_opened[key]
            if v.type == order_type and v.ticker == ticker:
                v.close(day, price)
                self.trades_closed[key] = v
                del self.trades_opened[key]
                money += v.init_capital + v.profit
                count += 1

        self.logger.info(str(count) + " trades close. Money free :" + str(money))
        return money

    def close_trade(self, k, day, price):
        v = self.trades_opened.pop(k)
        self.trades_closed[k] = v
        return v.init_capital + v.profit

    def get_current_profit(self, current_price, trade_type="all", ticker="all"):
        factor  = lambda t: 1.0 if t.type == "long" else -1.0
        open_price = (
            lambda trade, p: trade.num_actions
            * factor(trade) * (p - trade.open_price - trade.commission)
            - trade.slippage
        )

        if trade_type == "all":
            open_trade_prices = [
                (open_price(v, current_price), v.ticker) for k, v in self.trades_opened.items()
            ]
            close_trade_prices = [(v.profit, v.ticker) for k, v in self.trades_closed.items()]
        else:
            open_trade_prices = [
                (open_price(v, current_price), v.ticker)
                for k, v in self.trades_opened.items()
                if v.type == trade_type
            ]
            close_trade_prices = [
                (v.profit, v.ticker) for k, v in self.trades_closed.items() if v.type == trade_type
            ]
        if ticker != "all":
            open_trade_prices = [p for (p,t) in open_trade_prices if t == ticker]
            close_trade_prices = [p for (p,t) in close_trade_prices if t == ticker]
        else:
            open_trade_prices = [p for (p,t) in open_trade_prices]
            close_trade_prices = [p for (p,t) in close_trade_prices]
 
        return sum(open_trade_prices) + sum(close_trade_prices)

    def get_current_total_open(self, trade_type="all", ticker="all"):
        if trade_type == "all":
            open_trade_prices = [(v.init_capital, v.ticker) for k, v in self.trades_opened.items()]
            close_trade_prices = [(v.init_capital, v.ticker) for k, v in self.trades_closed.items()]
        else:
            open_trade_prices = [
                (v.init_capital, v.ticker)
                for k, v in self.trades_opened.items()
                if v.type == trade_type
            ]
            close_trade_prices = [
                (v.init_capital, v.ticker)
                for k, v in self.trades_closed.items()
                if v.type == trade_type
            ]

        if ticker != "all":
            open_trade_prices = [p for (p,t) in open_trade_prices if t == ticker]
            close_trade_prices = [p for (p,t) in close_trade_prices if t == ticker]
        else:
            open_trade_prices = [p for (p,t) in open_trade_prices]
            close_trade_prices = [p for (p,t) in close_trade_prices]

        return sum(open_trade_prices) + sum(close_trade_prices)

    def get_current_only_open(self, trade_type="all", ticker="all"):
        if trade_type == "all":
            open_trade_prices = [(v.init_capital, v.ticker) for k, v in self.trades_opened.items()]
        else:
            open_trade_prices = [
                (v.init_capital, v.ticker)
                for k, v in self.trades_opened.items()
                if v.type == trade_type
            ]
        if ticker != "all":
            open_trade_prices = [p for (p,t) in open_trade_prices if t == ticker]
        else:
            open_trade_prices = [p for (p,t) in open_trade_prices]

        return sum(open_trade_prices)

    def get_close_profit(self, trade_type="all", ticker="all"):
        if trade_type == "all":
            close_trade_prices = [(v.profit, v.ticker) for k, v in self.trades_closed.items()]
        else:
            close_trade_prices = [
                (v.profit, v.ticker) for k, v in self.trades_closed.items() if v.type == trade_type
            ]
        if ticker != "all":
            close_trade_prices = [p for (p,t) in close_trade_prices if t == ticker]
        else:
            close_trade_prices = [p for (p,t) in close_trade_prices]

        return sum(close_trade_prices)

    def get_close_trades_total_open(self, trade_type="all", ticker="all"):
        if trade_type == "all":
            close_trade_prices = [(v.init_capital, v.ticker) for k, v in self.trades_closed.items()]
        else:
            close_trade_prices = [
                (v.init_capital, v.ticker)
                for k, v in self.trades_closed.items()
                if v.type == trade_type
            ]
        if ticker != "all":
            close_trade_prices = [p for (p,t) in close_trade_prices if t == ticker]
        else:
            close_trade_prices = [p for (p,t) in close_trade_prices]

        return sum(close_trade_prices)

    def get_open_trades_total_open(self, trade_type="all", ticker="all"):
        if len(self.trades_opened) == 0:
            return 0

        if trade_type == "all":
            open_trade_prices = [(v.open_price, v.ticker) for k, v in self.trades_opened.items()]
        else:
            open_trade_prices = [
                (v.open_price, v.ticker)
                for k, v in self.trades_opened.items()
                if v.type == trade_type
            ]
        if ticker != "all":
            open_trade_prices = [p for (p,t) in open_trade_prices if t == ticker]
        else:
            open_trade_prices = [p for (p,t) in open_trade_prices]

        return sum(open_trade_prices)

    def get_close_profit_ratio(self, trade_type="all"):
        if trade_type == "all":
            profits = sum([trade.profit for key, trade in self.trades_closed.items()])
            init_capital = sum(
                [trade.open_price for key, trade in self.trades_closed.items()]
            )
            return profits / init_capital

        profits = sum(
            [
                trade.profit
                for key, trade in self.trades_closed.items()
                if trade.type == trade_type
            ]
        )
        init_capital = sum(
            [
                trade.open_price
                for key, trade in self.trades_closed.items()
                if trade.type == trade_type
            ]
        )
        return profits / init_capital

    def verify_stop_loss(self, day, min_price, max_price):
        money = 0
        for key in list(self.trades_opened.keys()):
            v = self.trades_opened[key]
            if v.type == "long":
                if (1 - v.stop_loss) * v.up_price > min_price:
                    self.logger.info(
                        str(day)
                        + " : "
                        + str(v.up_price)
                        + " - stop loss price: "
                        + str((1 - v.stop_loss) * v.up_price)
                        + " - min price: "
                        + str(min_price)
                    )
                    v.close(day, (1 - v.stop_loss) * v.up_price)
                    self.trades_closed[key] = v
                    money += v.init_capital + v.profit
                    del self.trades_opened[key]
                    self.logger.info(" trades close. Money free :" + str(money))
                else:
                    # increment days counter:
                    v.num_days += 1

                if v.stop_loss_trailing and max_price > v.up_price:
                    v.up_price = max_price
            else:
                if (1 + v.stop_loss) * v.up_price < max_price:
                    self.logger.info(
                        str(day)
                        + " : "
                        + str(v.up_price)
                        + " - stop loss price: "
                        + str((1 + v.stop_loss) * v.up_price)
                        + " - max price: "
                        + str(max_price)
                    )
                    v.close(day, (1 + v.stop_loss) * v.up_price)
                    self.trades_closed[key] = v
                    money += v.init_capital + v.profit
                    del self.trades_opened[key]
                    self.logger.info(" trades close. Money free :" + str(money))

                else:
                    # increment days counter:
                    v.num_days += 1

                if v.stop_loss_trailing and min_price < v.up_price:
                    v.up_price = max_price
        return money

    def clone(self, ticker):
        trade_list = TradeList(logging.WARNING)
        trade_list.trades_opened = {index:trade for index,trade in self.trades_opened.items() if trade.ticker == ticker}
        trade_list.trades_closed = {index:trade for index,trade in self.trades_closed.items() if trade.ticker == ticker}
        return trade_list
