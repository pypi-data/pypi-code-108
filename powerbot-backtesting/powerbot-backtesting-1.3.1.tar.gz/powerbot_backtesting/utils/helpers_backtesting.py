from datetime import datetime
from decimal import Decimal, getcontext
from typing import Union, ForwardRef

import pandas as pd

PositionStorage = ForwardRef("PositionStorage")


def _order_matching(side: str,
                    orderbook: pd.DataFrame,
                    timestamp: str,
                    price: Union[int, float],
                    quantity: Union[int, float, Decimal],
                    exec_orders_list: dict[str, int],
                    trade_list: list[dict],
                    contract_time: int,
                    vwap: float = None,
                    order_execution: str = "NON") -> Decimal:
    """
    Matches orders according to input parameters; adds trades made to trade_list and returns the remaining quantity.

    The order_execution parameter can be added to decide according to which logic the quantity should be filled. Allowed
    values are:

    NON - No restriction, partial execution is allowed

    FOK - Fill or Kill, if order isn't filled completely by first matching order, next matching order is loaded ->
    if none match next order book is loaded

    IOC - Immediate and Cancel, order is executed to maximum extent by first matching order, next order book is loaded ->
    allows price adjustments

    Args:
        side (str): buy/sell
        orderbook (pd.DataFrame): Single order book
        timestamp (str): Timestamp of order book
        price (int): Minimum/ Maximum Price for Transaction
        quantity (int): Quantity to buy/sell
        exec_orders_list (dict): Dictionary of already matched order IDs
        trade_list (list): List of executed trades
        contract_time (int): contract time in minutes, either 60, 30 or 15
        vwap (float): optional value to display current VWAP in the list of executed trades
        order_execution (str): Type of order execution that should be simulated

    Returns:
        Decimal: remaining quantity
    """
    # Transform Values to Decimals
    if (quantity := round(Decimal(quantity), 1)) <= 0: return quantity
    getcontext().prec = 8
    price = round(Decimal(price), 2)

    # Adjustments
    adjust_factor = {60: 1, 30: 2, 15: 4}
    mapping = {"buy": {"type": "ask", "op": -1, "asc": [True, False]},
               "sell": {"type": "bid", "op": 1, "asc": [False, False]}}

    orderbook = orderbook.loc[orderbook.type == mapping[side]["type"]].sort_values(by=['price', 'as_of'], ascending=mapping[side]["asc"])

    # Filter order book
    _order_matching_filter(orderbook, exec_orders_list)

    if orderbook.empty:
        return quantity

    for ind, row in orderbook.iterrows():
        if quantity > 0:
            open_qty = round(Decimal(row.quantity), 1)

            # Check If Price Is Matched
            price_match = Decimal(row["price"]) <= price if side == "buy" else Decimal(row["price"]) >= price

            if price_match:
                # If order can't be filled completely
                if order_execution == "FOK" and quantity > open_qty:
                    continue

                # Calculate quantities
                traded_quant = round(min(open_qty, quantity), 1)
                traded_power = traded_quant / adjust_factor[contract_time]

                # Calculate Cost
                cash = traded_quant * Decimal(row.price) * mapping[side]["op"] / adjust_factor[contract_time]

                trade_list[len([*trade_list]) + 1] = {"Side": side,
                                                      "Order ID": f"{row.order_id}",
                                                      "Quantity in MW": float(traded_quant),
                                                      "Power in MW/h": float(traded_power),
                                                      "Price": row["price"],
                                                      "Cash": round(float(cash), 2),
                                                      "Timestamp": timestamp} | ({"VWAP": round(vwap, 2)} if vwap else {})

                if row["order_id"] in [*exec_orders_list]:
                    # If Existing, Adjust Quantity
                    exec_orders_list[row["order_id"]] -= round(float(traded_quant), 1) * mapping[side]["op"]
                else:
                    exec_orders_list[row["order_id"]] = round(float(traded_quant), 1)

                quantity -= round(traded_quant, 1)  # Adjust Quantity

                # Break if quantity has been executed
                if order_execution == "IOC":
                    break

            else:
                break
        else:
            break

    return quantity


def _battery_order_matching_free(order_side: str,
                                 orderbook: pd.DataFrame,
                                 timestamp: str,
                                 price: Union[int, float],
                                 quantity: Union[int, float, Decimal],
                                 exec_orders_list: dict[str, int],
                                 trade_list: dict,
                                 position_storage: PositionStorage,
                                 order_execution: str = "NON") -> Decimal:
    """
    Matches orders according to input parameters; adds trades made to trade_list and returns the remaining quantity.

    The order_execution parameter can be added to decide according to which logic the quantity should be filled. Allowed
    values are:

    NON - No restriction, partial execution is allowed

    FOK - Fill or Kill, if order isn't filled completely by first matching order, next matching order is loaded ->
    if none match next order book is loaded

    IOC - Immediate and Cancel, order is executed to maximum extent by first matching order, next order book is loaded ->
    allows price adjustments

    Args:
        order_side (str): buy/sell
        orderbook (DataFrame): Single order book
        timestamp (str): Timestamp of order book
        price (int): Minimum/ Maximum Price for Transaction
        quantity (int): Quantity to buy/sell
        exec_orders_list (dict): Dictionary of already matched order IDs
        trade_list (list): List of executed trades
        position_storage (PositionStorage): Dict-like object to store positions
        order_execution (str): Type of order execution that should be simulated

    Returns:
        Decimal: remaining quantity
    """

    # Transform Values to Decimals
    factor = 100000
    price = int(price * factor)
    starting_quant = int(quantity * factor)
    quantity = int(quantity * factor)
    executed_trade = False

    cash_adjust = {60: 1, 30: 2, 15: 4}

    order_type = {"buy": "ask", "sell": "bid"}
    operator = {"buy": -1, "sell": 1}

    orderbook = orderbook.loc[orderbook.type == order_type[order_side]]

    if order_type[order_side] == "ask":
        orderbook = orderbook.sort_values(by=['price', 'as_of', 'del_period'], ascending=[True, False, True])
    else:
        orderbook = orderbook.sort_values(by=['price', 'as_of', 'del_period'], ascending=[False, False, True])

    # maybe try pandas apply
    for ind, row in orderbook.iterrows():
        if quantity > 0:
            open_qty = int(row["quantity"] * factor)

            if row.order_id in [*exec_orders_list]:  # Check If Already Matched
                if (saved_quant := int(exec_orders_list[row.order_id] * factor)) == open_qty:
                    continue  # Skip If Quantity Depleted
                open_qty = open_qty - saved_quant  # If Matched, Adjust Open Quantity

            # Check If Price Is Matched
            price_match = int(row.price * factor) <= price if order_side == "buy" else int(row.price * factor) >= price
            # print(order_side, price, int(row.price * factor), timestamp)

            if price_match:
                # If order can't be filled completely
                if order_execution == "FOK" and quantity > open_qty:
                    continue

                # Check if quantity is locked
                if position_storage.is_locked(timestamp):
                    continue

                # Check if we can buy quantity
                if order_side == "buy" and position_storage.available(timestamp) <= 0:
                    continue

                # Check if we have quantity to sell
                if order_side == "sell" and position_storage.filled(timestamp) <= 0:
                    continue

                traded_quant = min(open_qty, quantity)

                try:
                    if order_side == "buy":
                        position_storage.charge(row.del_period, round(traded_quant / factor, 1))
                    else:
                        position_storage.discharge(row.del_period, round(traded_quant / factor, 1))
                except ValueError:
                    continue

                # calculate contract period for cash adjustment
                periods = row.del_period.split(" - ")
                periods = [periods[0].split(" ")[-1], periods[-1]]
                delt = datetime.strptime(periods[1], "%H:%M") - datetime.strptime(periods[0], "%H:%M")
                contract_time = int(delt.seconds / 60)

                # Calculate Cost
                cash = traded_quant * row.price * operator[order_side] / cash_adjust[contract_time]

                trade_list[len([*trade_list]) + 1] = {"Side": order_side,
                                                      "Quantity": round(traded_quant / factor, 1),
                                                      "Price": row["price"],
                                                      "Cash": round(cash / factor, 2),
                                                      "Contract Delivery Period": row.del_period,
                                                      "Timestamp": timestamp}

                executed_trade = True

                print([i for i in position_storage.items()])

                if row.order_id in [*exec_orders_list]:
                    # If Existing, Adjust Quantity
                    if order_side == "buy":
                        exec_orders_list[row.order_id] += round(min(open_qty, quantity) / factor, 1)
                    else:
                        exec_orders_list[row.order_id] -= round(min(open_qty, quantity) / factor, 1)
                else:
                    exec_orders_list[row.order_id] = round(min(open_qty, quantity) / factor, 1)

                quantity -= traded_quant  # Adjust Quantity

                # Break if quantity has been executed
                if order_execution == "IOC":
                    break
            else:
                break
        else:
            break

    return round((starting_quant - quantity) / factor, 2) if executed_trade else 0


def _battery_order_matching_linked(orderbook: pd.DataFrame,
                                   timestamp: str,
                                   min_price: Union[int, float],
                                   max_perc: float,
                                   exec_orders_list: dict[str, int],
                                   trade_list: dict,
                                   position_storage: PositionStorage,
                                   min_spread: Union[float, int] = 2):
    """
    Matches orders according to input parameters and adds trades made to trade_list.

    Args:
        orderbook (DataFrame): Single order book
        timestamp (str): Timestamp of order book
        min_price (int): Minimum/ Maximum Price for Transaction
        max_perc (float): Maximum percentage of maximum capacity that can be used for a single order
        exec_orders_list (dict): Dictionary of already matched order IDs
        trade_list (list): List of executed trades
        position_storage (PositionStorage): Dict-like object to store positions
        min_spread (float/int): Minimum price difference between linked positions
    """
    # Values
    max_amount = position_storage.max_cap * max_perc

    # Adjust quantities and filter out depleted orders
    _order_matching_filter(orderbook, exec_orders_list)
    orderbook = orderbook.loc[orderbook.quantity > 0.01]

    # Split into bids & asks with correct prices
    orderbook_ask = orderbook.loc[(orderbook.type == "ask") & (orderbook.price <= min_price)].sort_values(
        by=['price', 'as_of', 'del_period'],
        ascending=[True, False, True])
    orderbook_bid = orderbook.loc[(orderbook.type == "bid") & (orderbook.price >= min_price + min_spread)].sort_values(
        by=['price', 'as_of', 'del_period'], ascending=[False, False, True])

    # If one is empty -> linking impossible
    if any(o.empty for o in [orderbook_ask, orderbook_bid]):
        return

    # Determine the best buy order
    if (position := position_storage.available((buy := orderbook_ask.iloc[0]).del_period)) < 0.01:
        return

    # Order Linking
    match = orderbook_bid.loc[
        (orderbook_bid.del_period > buy.del_period) & (orderbook_bid.price - buy.price >= min_spread) & (orderbook_bid.quantity >= buy.quantity)]

    if isinstance((sell := None if match.empty else match.iloc[0]), pd.Series):
        # Check if either quantity is locked
        if any(position_storage.is_locked(i.del_period) for i in [buy, sell]):
            return

        # Adjust both orders
        buy = _adjust_to_del_unit(buy)
        sell = _adjust_to_del_unit(sell)

        traded_power = round(min(buy._quantity, sell._quantity, position, max_amount), 3)
        traded_quant = buy.factor * traded_power

        try:
            position_storage.charge(buy.del_period, traded_power)
            position_storage.discharge(sell.del_period, traded_power)
        except ValueError as e:
            if "not loaded" in str(e):
                position_storage.discharge(buy.del_period, traded_power)

        # Calculate Cost
        for name, order in {"buy": buy, "sell": sell}.items():
            trade_list[len([*trade_list]) + 1] = {"Side": name,
                                                  "Order ID": f"{order.order_id}",
                                                  "Quantity in MW": traded_quant,
                                                  "Power in MW/h": traded_power,
                                                  "Price per MW": order.price,
                                                  "Cash": round(traded_quant * order._price, 2) * (-1 if name == "buy" else 1),
                                                  "Contract Delivery Period": order.del_period,
                                                  "Timestamp": timestamp}

            if order.order_id in [*exec_orders_list]:
                # If Existing, Adjust Quantity
                exec_orders_list[order.order_id] += round(traded_quant * (-1 if name == "buy" else 1), 1)
            else:
                exec_orders_list[order.order_id] = round(traded_quant * (-1 if name == "buy" else 1), 1)


def _adjust_to_del_unit(order: pd.Series) -> pd.Series:
    """
    Function that adds additional information to an order according to the delivery unit of the contract.

    Args:
        order (pd.Series): order from order book

    Returns:
        pd.Series
    """
    adjust_factor = {3600: 1, 1800: 2, 900: 4}

    # Calculation order delivery unit
    time_period = order.del_period.split(" ")
    start = datetime.strptime(f"{time_period[0]} {time_period[1]}", "%Y-%m-%d %H:%M")
    end = datetime.strptime(f"{time_period[0]} {time_period[-1]}", "%Y-%m-%d %H:%M")

    # Adjusting order
    order.factor = adjust_factor[(end - start).seconds]
    order._quantity = order.quantity / order.factor
    order._price = order.price / order.factor

    return order


def _order_matching_filter(df: pd.DataFrame, matched: dict[str, float]) -> None:
    """
    Function to filter an order book against a dictionary of already matched orders.

    Will replace quantities accordingly if not exhausted already.

    Args:
        df (pd.DataFrame): orderbook
        matched (dict): dictionary of already matched orders
    """
    # Check If Already Matched
    for nr in df.loc[df.order_id.isin(matched)].index:
        df.at[nr, "quantity"] += round(matched[df.loc[nr].order_id], 1)
