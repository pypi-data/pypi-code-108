from typing import Any, Dict, Optional

from nautilus_trader.adapters.binance.common import format_symbol
from nautilus_trader.adapters.binance.http.api.spot_account import BinanceSpotAccountHttpAPI
from nautilus_trader.adapters.binance.http.enums import NewOrderRespType


class BinanceFutureAccountHttpAPI(BinanceSpotAccountHttpAPI):

    BASE_ENDPOINT = "/fapi/v1/"

    async def position_mode(self, recv_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get current position mode on EVERY symbol

        `GET /fapi/v1/positionSide/dual`.

        Parameters
        ----------
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        ----------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#get-current-position-mode-user_data

        """
        payload: Dict[str, str] = {}
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "positionSide/dual",
            payload=payload,
        )

    async def change_position_mode(
        self,
        dual_side_position: bool,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Change user's position mode on EVERY symbol

        `POST /fapi/v1/positionSide/dual`.

        Parameters
        ----------
        dual_side_position : bool
            "true": Hedge Mode; "false": One-way Mode
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        ----------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#change-position-mode-trade

        """
        payload: Dict[str, str] = {
            "dualSidePosition": str(dual_side_position).lower(),
        }

        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT + "positionSide/dual",
            payload=payload,
        )

    async def multi_assets_mode(self, recv_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user's Multi-Assets mode (Multi-Assets Mode or Single-Asset Mode) on Every symbol

        `GET /fapi/v1/multiAssetsMargin`.

        Parameters
        ----------
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        ----------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#get-current-multi-assets-mode-user_data

        """
        payload: Dict[str, str] = {}
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "multiAssetsMargin",
            payload=payload,
        )

    async def change_multi_assets_mode(
        self,
        multi_assets_mode: bool,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Change user's Multi-Assets mode (Multi-Assets Mode or Single-Asset Mode) on Every symbol

        `POST /fapi/v1/multiAssetsMargin`.

        Parameters
        ----------
        multi_assets_mode : bool
            "true": Multi-Assets Mode; "false": Single-Asset Mode
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        ----------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#change-multi-assets-mode-trade

        """
        payload: Dict[str, str] = {
            "multiAssetsMargin": str(multi_assets_mode).lower(),
        }
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT + "multiAssetsMargin",
            payload=payload,
        )

    async def new_order(  # noqa: C901
        self,
        symbol: str,
        side: str,
        type: str,
        position_side: Optional[str] = None,
        time_in_force: Optional[str] = None,
        quantity: Optional[str] = None,
        reduce_only: Optional[bool] = None,
        price: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        stop_price: Optional[str] = None,
        close_position: Optional[bool] = None,
        activation_price: Optional[str] = None,
        callback_rate: Optional[str] = None,
        working_type: Optional[str] = None,
        price_protect: Optional[bool] = None,
        new_order_resp_type: NewOrderRespType = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Submit a new order.

        Submit New Order (TRADE).
        `POST /fapi/v1/order`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        side : str
            The order side for the request.
        type : str
            The order type for the request.
        position_side : str, optional
            Default BOTH for One-way Mode ; LONG or SHORT for Hedge Mode. It must be sent in Hedge Mode.
        time_in_force : str, optional
            The order time in force for the request.
        quantity : str, optional
            The order quantity in base asset units for the request.
        reduce_only : bool, optional
            Reduce "true" or "false". default "false". Cannot be sent in Hedge Mode; cannot be sent with closePosition=true
        price : str, optional
            The order price for the request.
        new_client_order_id : str, optional
            The client order ID for the request. A unique ID among open orders.
            Automatically generated if not provided.
        stop_price : str, optional
            The order stop price for the request.
            Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
        close_position : bool, optional
            Close position true, false；Close-All，used with STOP_MARKET or TAKE_PROFIT_MARKET.
        activation_price: str, optional
            Used with TRAILING_STOP_MARKET orders, default as the latest price(supporting different workingType)
        callback_rate: str, optional
            Used with TRAILING_STOP_MARKET orders, min 0.1, max 5 where 1 for 1%
        working_type: str, optional
            stopPrice triggered by: "MARK_PRICE", "CONTRACT_PRICE". Default "CONTRACT_PRICE"
        price_protect: str, optional
            "TRUE" or "FALSE", default "FALSE". Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
        new_order_resp_type : NewOrderRespType, optional
            The response type for the order request.
            MARKET and LIMIT order types default to FULL, all other orders default to ACK.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#new-order-trade

        """
        payload: Dict[str, str] = {
            "symbol": format_symbol(symbol).upper(),
            "side": side,
            "type": type,
        }
        if position_side is not None:
            payload["positionSide"] = position_side
        if time_in_force is not None:
            payload["timeInForce"] = time_in_force
        if quantity is not None:
            payload["quantity"] = quantity
        if reduce_only is not None:
            payload["reduceOnly"] = str(reduce_only).lower()
        if price is not None:
            payload["price"] = price
        if new_client_order_id is not None:
            payload["newClientOrderId"] = new_client_order_id
        if stop_price is not None:
            payload["stopPrice"] = stop_price
        if close_position is not None:
            payload["closePosition"] = str(close_position).lower()
        if activation_price is not None:
            payload["activationPrice"] = activation_price
        if callback_rate is not None:
            payload["callbackRate"] = callback_rate
        if working_type is not None:
            payload["workingType"] = working_type
        if price_protect is not None:
            payload["priceProtect"] = str(price_protect).upper()
        if new_order_resp_type is not None:
            payload["newOrderRespType"] = new_order_resp_type.value
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT + "order",
            payload=payload,
        )

    async def cancel_open_orders(
        self,
        symbol: str,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Cancel all active orders on a symbol. This includes OCO orders.

        Cancel all Open Orders on a Symbol (TRADE).
        `DELETE /fapi/v1/allOpenOrders`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#cancel-all-open-orders-on-a-symbol-trade

        """
        payload: Dict[str, str] = {"symbol": format_symbol(symbol).upper()}
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="DELETE",
            url_path=self.BASE_ENDPOINT + "allOpenOrders",
            payload=payload,
        )

    async def account(self, recv_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get current account information.

        Account Information (USER_DATA).
        `GET /fapi/v2/account`.

        Parameters
        ----------
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#account-information-v2-user_data

        """
        payload: Dict[str, str] = {}
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path="/fapi/v2/" + "account",
            payload=payload,
        )

    async def balance(self, recv_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get current balance information.

        Balance Information (USER_DATA).
        `GET /fapi/v2/balance`.

        Parameters
        ----------
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#futures-account-balance-v2-user_data

        """
        payload: Dict[str, str] = {}
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path="/fapi/v2/" + "balance",
            payload=payload,
        )

    async def change_leverage(
        self, symbol: str, leverage: int, recv_window: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Change user's initial leverage of specific symbol market.

        `POST /fapi/v1/leverage`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        leverage : int
            Target initial leverage: int from 1 to 125
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#change-initial-leverage-trade

        """
        payload: Dict[str, str] = {
            "symbol": format_symbol(symbol).upper(),
            "leverage": str(leverage),
        }
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT + "leverage",
            payload=payload,
        )

    async def change_margin_type(
        self, symbol: str, margin_type: str, recv_window: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Change margin type for symbol

        `POST /fapi/v1/marginType`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        margin_type : str
            ISOLATED, CROSSED
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#change-margin-type-trade

        """
        payload: Dict[str, str] = {
            "symbol": format_symbol(symbol).upper(),
            "marginType": margin_type,
        }
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT + "marginType",
            payload=payload,
        )

    async def modify_isolated_position_margin(
        self,
        symbol: str,
        amount: str,
        type: int,
        position_side: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Modify Isolated Position Margin

        `POST /fapi/v1/positionMargin`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        amount : str
            Amount
        type : int
            1: Add position margin，2: Reduce position margin
        position_side : str, optional
            Default BOTH for One-way Mode ; LONG or SHORT for Hedge Mode. It must be sent with Hedge Mode.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#modify-isolated-position-margin-trade

        """
        payload: Dict[str, str] = {
            "symbol": format_symbol(symbol).upper(),
            "amount": amount,
            "type": str(type),
        }

        if position_side is not None:
            payload["positionSide"] = position_side
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT + "positionMargin",
            payload=payload,
        )

    async def position_margin_change_history(
        self,
        symbol: str,
        type: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get Position Margin Change History (TRADE)

        `GET /fapi/v1/positionMargin/history`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        type : int, optional
            1: Add position margin，2: Reduce position margin
        start_time : int, optional
            The start time (UNIX milliseconds) filter for the request.
        end_time : int, optional
            The end time (UNIX milliseconds) filter for the request.
        limit : int, optional
            The limit for the response.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#get-position-margin-change-history-trade

        """
        payload: Dict[str, str] = {
            "symbol": format_symbol(symbol).upper(),
        }
        if type is not None:
            payload["type"] = str(type)
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if limit is not None:
            payload["limit"] = str(limit)
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "positionMargin/history",
            payload=payload,
        )

    async def position(
        self, symbol: Optional[str] = None, recv_window: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get current position information.

        `GET /fapi/v2/positionRisk`.

        Parameters
        ----------
        symbol : str, optional
            The symbol for the request.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#position-information-v2-user_data

        """
        payload: Dict[str, str] = {}
        if symbol is not None:
            payload["symbol"] = format_symbol(symbol).upper()
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path="/fapi/v2/" + "positionRisk",
            payload=payload,
        )

    async def my_trades(
        self,
        symbol: str,
        from_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get trades for a specific account and symbol.

        Account Trade List (USER_DATA)
        `GET /fapi/v1/userTrades`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        from_id : str, optional
            The trade match ID to query from.
        start_time : int, optional
            The start time (UNIX milliseconds) filter for the request.
        end_time : int, optional
            The end time (UNIX milliseconds) filter for the request.
        limit : int, optional
            The limit for the response.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#account-trade-list-user_data

        """
        payload: Dict[str, str] = {"symbol": format_symbol(symbol).upper()}
        if from_id is not None:
            payload["fromId"] = from_id
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if limit is not None:
            payload["limit"] = str(limit)
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "userTrades",
            payload=payload,
        )

    async def commission_rate(
        self,
        symbol: str,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        User Commission Rate (USER_DATA)

        `GET /fapi/v1/commissionRate`.

        Parameters
        ----------
        symbol : str
            The symbol for the request.
        recv_window : int, optional
            The response receive window for the request (cannot be greater than 60000).

        Returns
        -------
        dict[str, Any]

        References
        ----------
        https://binance-docs.github.io/apidocs/futures/en/#user-commission-rate-user_data

        """
        payload: Dict[str, str] = {"symbol": format_symbol(symbol).upper()}
        if recv_window is not None:
            payload["recvWindow"] = str(recv_window)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "commissionRate",
            payload=payload,
        )
