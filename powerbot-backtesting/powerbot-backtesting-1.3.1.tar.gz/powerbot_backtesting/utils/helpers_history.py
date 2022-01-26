import json

import pandas as pd

from powerbot_backtesting.utils.constants import *


def _historic_contract_transformation(path_to_file: str, exchange: str) -> pd.DataFrame:
    if exchange in SYSTEMS["M7"]:
        index = pd.json_normalize(json.load(open(path_to_file)))[
            ["deliveryAreas", "deliveryEnd", "deliveryStart", "details.contractId", "details.prod", "details.actPoint",
             "details.expPoint", "details.undrlngContracts.contractId"]]
    else:
        index = pd.DataFrame(json.load(open(path_to_file)))
        index.rename(columns={"_id": "contract_id", "product": "_product"}, inplace=True)

    index.rename(columns={"details.contractId": 'contract_id', "deliveryAreas": 'delivery_areas',
                          "deliveryStart": 'delivery_start', "deliveryEnd": 'delivery_end',
                          "details.prod": '_product', "details.actPoint": 'activation_time',
                          "details.expPoint": 'expiry_time', 'details.undrlngContracts.contractId': 'undrlng_contracts'},
                 inplace=True)

    return index


def _historic_data_transformation(files: list, exchange: str, filetype: str) -> pd.DataFrame:
    """
    Function transforms historic data into correct format to be used with other data processing functions.

    Args:
        files (list): List of files to be transformed
        exchange (str): Exchange e.g. epex, nordpool, southpool, etc.
        filetype (str): either trades or orders

    Returns:
        pd.DataFrame
    """
    # Append contracts that are in the same timeframe to one DataFrame
    lst = []
    for file in files:
        lst.append(pd.read_json(file))
    df = pd.concat(lst, ignore_index=True)

    if exchange in SYSTEMS["M7"]:
        if filetype == "trades":
            df.drop(columns=["revisionNo"], inplace=True)
            df.rename(columns={"_id": "trade_id", "contractId": 'contract_id', "tradeExecTime": 'exec_time',
                               "apiTimeStamp": 'api_timestamp', "buyDeliveryArea": 'buy_delivery_area',
                               "sellDeliveryArea": 'sell_delivery_area', "selfTrade": 'self_trade',
                               "qty": 'quantity', "px": 'price', "pxqty": 'prc_x_qty'},
                      inplace=True)

            df.quantity = df.quantity / 1000
            df.price = df.price / 100
            df.prc_x_qty = round(df.prc_x_qty / 100000, 2)

        if filetype == "orders":
            df.rename(columns={"asOf": "as_of", "bestAskPrice": "best_ask", "bestAskQuantity": "best_ask_qty",
                               "bestBidPrice": "best_bid", "bestBidQuantity": "best_bid_qty",
                               "contractId": "contract_id", "deliveryArea": "delivery_area", "full": "delta",
                               "lastPrice": "last_price", "lastQuantity": "last_qty",
                               "lastUpdate": "last_trade_time", "revisionNo": "revision_no"},
                      inplace=True)

            # Getting information from details field if missing on upper level
            meta_cols = {"best_bid": "bestBidPx", "best_ask": "bestAskPx", "best_bid_qty": "bestBidQty",
                         "last_price": "lastPx", "last_qty": "lastQty", "last_trade_time": "lastTradeTime",
                         "volume": "totalQty", "high": "highPx", "low": "lowPx", "revision_no": "revisionNo"}
            missing_details = {k: v for k, v in meta_cols.items() if k not in df.columns}
            details = df.details.tolist()

            for k, v in missing_details.items():
                if v in ["lastPx", "lastQty", "highPx", "lowPx", "totalQty"]:
                    df[k] = [i[v] / 100 if v in [*i] else None for i in details]
                else:
                    df[k] = [i[v] if v in [*i] else None for i in details]

            contract_id = df.contract_id.unique().tolist()[0]
            delivery_area = df.delivery_area.unique().tolist()[0]
            asks = [i["sellOrdrList"]["ordrBookEntry"] if i["sellOrdrList"] else None for i in df.details.tolist()]
            bids = [i["buyOrdrList"]["ordrBookEntry"] if i["buyOrdrList"] else None for i in df.details.tolist()]

            conversion = lambda i: [{"order_id": v["ordrId"], "price": v["px"] / 100, "quantity": v["qty"] / 1000,
                                     "contract_id": contract_id, "delivery_area": delivery_area,
                                     "order_entry_time": v["ordrEntryTime"]} for v in i]

            asks = [conversion(i) if i else None for i in asks]
            bids = [conversion(i) if i else None for i in bids]

            df["asks"] = asks
            df["bids"] = bids
            df.delta = [False if i else True for i in df.delta]
            df.drop(columns=["_id", "details", "avwa", "bvwa"], inplace=True, errors="ignore")

    else:
        if filetype == "trades":
            # Filter out deleted Trades
            df = df.loc[~df.deleted]

            df.rename(columns={"_id": "trade_id", "tradeTime": 'exec_time', "apiTimestamp": "api_timestamp",
                               "companyTrade": "self_trade"},
                      inplace=True)

            details = df.legs.tolist()

            df["contract_id"] = [i[0]["contractId"] for i in details]
            df["buy_delivery_area"] = [NORDPOOL_EIC_CODES[i[0]["deliveryAreaId"]] if i else None for i in
                                       details]
            df["sell_delivery_area"] = [NORDPOOL_EIC_CODES[i[1]["deliveryAreaId"]] if len(i) == 2 else None for
                                        i in
                                        details]
            df["quantity"] = [float(i[0]["quantity"]) for i in details]
            df["price"] = [float(i[0]["unitPrice"]) for i in details]
            df["prc_x_qty"] = round(df.price * df.quantity, 2)

            df.drop(columns=["eventSequenceNo", "legs", "mediumDisplayName", "deleted", "state"], inplace=True)

        if filetype == "orders":
            df.rename(
                columns={"apiTimestamp": "as_of", "bestAskPrice": "best_ask", "bestAskQuantity": "best_ask_qty",
                         "bestBidPrice": "best_bid", "bestBidQuantity": "best_bid_qty", "bidsAndAsks": "details",
                         "contractId": "contract_id", "deliveryArea": "delivery_area", "full": "delta",
                         "lastPrice": "last_price", "lastQuantity": "last_qty", "lowestPrice": "low",
                         "highestPrice": "high", "lastTradeTime": "last_trade_time", "revision": "revision_no",
                         "turnover": "total_quantity"},
                inplace=True)

            df = df.astype({"contract_id": "str"})

            df["delta"] = [False if "snapshot" in i else True for i in df.details]
            df.revision_no = [i for i in range(0, len(df))]
            df.delivery_area = [NORDPOOL_EIC_CODES[i] for i in df.delivery_area.tolist()]
            asks = [i["asks"] if "asks" in i else None for i in df.details.tolist()]
            bids = [i["bids"] if "bids" in i else None for i in df.details.tolist()]

            conversion = lambda i: [
                {"order_id": str(v["orderId"]), "price": float(v["price"]), "quantity": float(v["quantity"]),
                 "contract_id": str(v["contractId"]), "delivery_area": NORDPOOL_EIC_CODES[v["deliveryArea"]],
                 "order_entry_time": v["createdAt"]} for v in i]

            df["asks"] = [conversion(i) if i else None for i in asks]
            df["bids"] = [conversion(i) if i else None for i in bids]

            df.drop(columns=["_id", "details", "updatedAt"], inplace=True)

    return df
