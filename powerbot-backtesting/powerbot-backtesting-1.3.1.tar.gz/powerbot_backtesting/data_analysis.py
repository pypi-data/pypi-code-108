from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from powerbot_backtesting.utils import _order_matching
from powerbot_backtesting.utils.constants import *


def flexpos_algo(orderbooks: dict[str, pd.DataFrame],
                 marg_prices: list[float],
                 buy_sell_spread: list[float],
                 init_prod: list[float],
                 min_prod: list[float],
                 max_prod: list[float],
                 closing_from: int = 2,
                 marg_prices_pc: list[list[float]] = None) -> dict[str, dict]:
    """
    Algorithm that connects a flexibility algorithm with a position closer. At the defined timestamp, the flexibility
    algo is replaced with the position closer algo, which tries to close a position with the provided information.

    Timestamps are not directly passed as arguments, but rather inferred by the closing_from parameter, which calculates
    the respective start times for the position closer based on the closing_from value and the delivery start of the
    contract.

    Args:
        orderbooks (dict{key: DataFrame}): Dictionary of Orderbooks
        marg_prices (list[float]): Marginal Price to fluctuate around/ close position
        buy_sell_spread (list[float]): Minimum Profit per MW
        init_prod (list[float]): Initial Quantity of produced MW
        min_prod (list[float]): Minimum Quantity of produced MW
        max_prod (list[float]): Maximum Quantity of produced MW
        closing_from (int): Amount of hours before contract delivery start algorithm should stop running at
        marg_prices_pc (list[list[float]]): Marginal prices specific for position closer (optional)

    Returns:
        dict[key: dict[Production_quant (float), Remaining_quant (float), Profit (float),
            Trades_Flex (list), Trades_PC (list)]]
    """

    # Checking Parameters
    if not all(len(i) == len([*orderbooks]) for i in [marg_prices, buy_sell_spread, init_prod, min_prod, max_prod]):
        raise Exception(f"All parameters have to be same length as amount of contracts in orderbook!")

    # Executing Flex Algo
    results_flex = flex_algo(orderbooks, marg_prices, buy_sell_spread, init_prod, min_prod, max_prod, closing_from)

    # Setup for PC Algo
    positions = [v["Production"] for v in results_flex.values()]
    start_from = [datetime.strptime(i.replace(f"{str(i).split(' - ')[1]}", "").replace(" - ", ":00"), DATE_YMD_TIME_HMS)
                  for i in [*orderbooks]]
    orderbooks_pc = {key: {} for key in [*orderbooks]}

    for nr, (timestamp, contract) in enumerate(orderbooks.items()):
        for key, orderbook in contract.items():
            if datetime.strptime(key, DATE_YMD_TIME_HMS_TZ) >= start_from[nr].replace(tzinfo=timezone.utc):
                orderbooks_pc[timestamp][key] = orderbook
    marg_prices_pc = [[i, i] for i in marg_prices] if not marg_prices_pc else marg_prices_pc

    # Executing PC Algo
    results_pc = pc_algo(orderbooks_pc, positions, marg_prices_pc)

    # Summing up Results
    results_total = {
        key: {"Initial_quant": init_prod[nr], "Flex_quant": results_flex[key]["Production"], "Remaining_quant": 0,
              "Profit": results_flex[key]["Profit"], "Trades_Flex": results_flex[key]["Trades"]} for nr, key in
        enumerate([*results_flex])}

    for key, contract in results_pc.items():
        for name, value in contract.items():
            if name == "Remaining_quant":
                results_total[key]["Remaining_quant"] = value
            if name == "Cash":
                results_total[key]["Profit"] = results_total[key]["Profit"] + Decimal(value)
            if name == "Trades":
                results_total[key]["Trades_PC"] = value

    return results_total


def flex_algo(orderbooks: dict[str, pd.DataFrame],
              marg_prices: list[float],
              buy_sell_spread: list[float],
              init_prod: list[float],
              min_prod: list[float],
              max_prod: list[float],
              closing_from: int = None) -> dict[str, dict]:
    """
    Standard flexibility algorithm that aims to maximize profit by fluctuating around a marginal price.
    All parameters have to be given as lists of the same length as the amount of contracts in orderbooks.

    Args:
        orderbooks (dict{key: DataFrame}): Dictionary of Orderbooks
        marg_prices (list): Marginal Price to fluctuate around
        buy_sell_spread (list): Minimum Profit per KWh
        init_prod (list): Initial Quantity of produced MW
        min_prod (list): Minimum Quantity of produced MW
        max_prod (list): Maximum Quantity of produced MW
        closing_from (int): Amount of hours before contract delivery start algorithm should stop running at
            (only relevant for flexpos_algo)

    Returns:
        dict[key: dict[Production (float), Profit (float), Trades (list)]]
    """
    # Setup
    trade_list = {key: {} for key in [*orderbooks]}
    results = {key: {} for key in [*orderbooks]}
    closing_timestamps = [
        datetime.strptime(i.replace(f"{str(i).split(' - ')[1]}", "").replace(" - ", ":00"), DATE_YMD_TIME_HMS) for i
        in [*orderbooks]] if closing_from else None

    for nr, (key, contract) in enumerate(orderbooks.items()):
        exec_orders_list = {}
        curr_prod = init_prod[nr]
        contract_time = key.split(" ")
        contract_time = int((datetime.strptime(contract_time[3], TIME_HM) - datetime.strptime(contract_time[1],
                                                                                              TIME_HM)).seconds / 60)

        for timestamp, orderbook in contract.items():
            # Stopping Loop on closing Timestamp
            if closing_from and datetime.strptime(timestamp, DATE_YMD_TIME_HMS_TZ) >= closing_timestamps[nr].replace(tzinfo=timezone.utc):
                break
            # Buy
            if round(max_prod[nr] - curr_prod, 1) > 0.1:
                rem_quant_buy = _order_matching("buy", orderbook, timestamp, marg_prices[nr] - buy_sell_spread[nr],
                                                max_prod[nr] - curr_prod, exec_orders_list, trade_list[key],
                                                contract_time)

                curr_prod = max_prod[nr] - rem_quant_buy  # If Remaining Quantity. Subtract From Maximum

            # Sell
            if round(curr_prod - min_prod[nr], 1) > 0.1:
                rem_quant_sell = _order_matching("sell", orderbook, timestamp, marg_prices[nr] + buy_sell_spread[nr],
                                                 curr_prod - min_prod[nr], exec_orders_list, trade_list[key],
                                                 contract_time)

                curr_prod = min_prod[nr] + rem_quant_sell  # If Remaining Quantity, Add To Minimum

        cash = Decimal(sum([value["Cash"] for value in trade_list[key].values()]))  # Calculating Cash

        results[key]["Production"] = curr_prod
        results[key]["Profit"] = round(curr_prod * marg_prices[nr] - abs(cash), 2)
        results[key]["Trades"] = trade_list[key]

    return results


def pc_algo(orderbooks: dict[str, pd.DataFrame],
            positions: list[float],
            marg_prices: list[list[int]] = None) -> dict[str, dict]:
    """
    Standard position closing algorithm that aims to close an open position, optionally taking a marginal price into
    consideration. Positional values have to match the amount of keys in the orderbooks in length (1 position per contract).

    Things to consider:
    This algorithm is best used with either a single orderbook for a certain timestamp that a position should be closed
    at or multiple orderbooks beginning from this timestamp. This simulates closing the position at the desired time.
    Alternatively, the flexpos_algo can be used to try to maximize profit before the position is closed.

    Args:
        orderbooks (dict{key: DataFrame}): Dictionary of Orderbooks
        positions (list): Positional values in MW (1 position per contract)
        marg_prices (list): List with 2 values representing the minimum amount an order can be matched with (bought or sold)

    Returns:
        dict[key: dict[Initial_quant (int/float), Remaining_quant (float), Cash (float), Trades (list)]]
    """
    # Orderbooks dict object consists of keys for each contract with the aggregated orderbooks as dataframes attached

    # Checking Values
    if not isinstance(positions, list) or len(positions) != len([*orderbooks]):
        raise Exception("Parameter positions has to be list of floats of same length as contracts in orderbook!")

    if marg_prices:
        if not isinstance(marg_prices, list) or not all(len(i) == 2 for i in marg_prices):
            raise Exception("Marginal prices have to be provided as a list, containing 2 floats/integers representing"
                            " buy price and sell price!")
    else:
        marg_prices = [[1000, 0] for _ in [*orderbooks]]

    # Setup
    exec_orders_list = {}
    trade_list = {key: {} for key in [*orderbooks]}
    results = {key: {"Initial_quant": positions[nr], "Remaining_quant": 0, "Cash": 0, "Trades": []} for nr, key in
               enumerate([*orderbooks])}

    for nr, (key, contract) in enumerate(orderbooks.items()):
        pos = positions[nr]
        buy_price = marg_prices[nr][0]
        sell_price = marg_prices[nr][1]
        contract_time = key.split(" ")
        contract_time = int((datetime.strptime(contract_time[3], TIME_HM) - datetime.strptime(contract_time[1],
                                                                                              TIME_HM)).seconds / 60)

        if isinstance(contract, pd.DataFrame) and contract.empty or not contract:
            results[key]["Remaining_quant"] = "No data"
            continue

        for timestamp, orderbook in contract.items():
            # Buy
            if pos < 0:
                pos = -(_order_matching("buy", orderbook, timestamp, buy_price, abs(pos), exec_orders_list,
                                        trade_list[key], contract_time))

            # Sell
            elif pos > 0:
                pos = _order_matching("sell", orderbook, timestamp, sell_price, pos, exec_orders_list, trade_list[key],
                                      contract_time)

            else:
                break
        if pos:
            results[key]["Remaining_quant"] = round(pos, 1)

    for contract, trades in trade_list.items():
        results[contract]["Cash"] = round(sum([value["Cash"] for value in trades.values()]), 2)
        results[contract]["Trades"] = trades

    return results
