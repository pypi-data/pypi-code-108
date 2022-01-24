from typing import Any, Dict, Optional

from nautilus_trader.core.correctness import PyCondition

from nacre.adapters.zb.common import format_market
from nacre.adapters.zb.http.spot import ZbSpotHttpClient


class ZbSpotAccountHttpAPI:
    BASE_ENDPOINT = "/api/"

    def __init__(self, client: ZbSpotHttpClient):
        """
        Initialize a new instance of the ``ZbSpotAccountHttpAPI`` class.

        Parameters
        ----------
        client : ZbSpotHttpClient
            The Binance REST API client.

        """
        PyCondition.not_none(client, "client")

        self.client = client

    async def get_account(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getAccountInfo",
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getAccountInfo",
            payload=payload,
        )

    async def get_user_address(self, currency: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getUserAddress",
            "currency": format_market(currency),
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getUserAddress",
            payload=payload,
        )

    async def get_payin_address(self, currency: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getPayinAddress",
            "currency": format_market(currency),
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getPayinAddress",
            payload=payload,
        )

    async def get_withdraw_address(self, currency: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getWithdrawAddress",
            "currency": format_market(currency),
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getWithdrawAddress",
            payload=payload,
        )

    async def get_withdraw_record(
        self,
        currency: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getWithdrawRecord",
            "currency": format_market(currency),
        }
        if page_index is not None:
            payload["pageIndex"] = str(page_index)
        if page_size is not None:
            payload["pageSize"] = str(page_size)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getWithdrawRecord",
            payload=payload,
        )

    async def get_charge_record(
        self,
        currency: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getChargeRecord",
            "currency": format_market(currency),
        }
        if page_index is not None:
            payload["pageIndex"] = str(page_index)
        if page_size is not None:
            payload["pageSize"] = str(page_size)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getChargeRecord",
            payload=payload,
        )

    async def get_fee_info(self, currency: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getFeeInfo",
            "currency": format_market(currency),
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getFeeInfo",
            payload=payload,
        )

    async def withdraw(
        self,
        amount: float,
        currency: str,
        fees: float,
        receive_addr: str,
        safe_pwd: str,
        itransfer: Optional[int] = 1,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "withdraw",
            "amount": amount,
            "currency": format_market(currency),
            "fees": fees,
            "itransfer": itransfer,
            "receiveAddr": receive_addr,
            "safePwd": safe_pwd,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "withdraw",
            payload=payload,
        )

    async def order(
        self,
        amount: float,
        currency: str,
        price: float,
        trade_type: int,
        customer_order_id: Optional[str] = None,
        order_type: Optional[int] = None,
        acct_type: int = 0,
    ) -> Dict[str, Any]:
        """
        Submit a new order.

        Parameters
        ----------
        amount : float
            Amount
        currency : str
            Symbol
        price :  float
            Price
        trade_type : int
            Transaction type, 1 for buy, 0 for sell
        customer_order_id : str, optional
            User defined ID, 4-36 characters, consisting of numbers or letters
        order_type : str, optional
            Delegate type, 1 for PostOnly, 2 for IOC, None for Limit
        acct_type : int, optional
            Mode, 0 for spot, 1 for isolated margin, 2 for cross magin, default spot

        Returns
        -------
        dict[str, Any]

        """
        payload: Dict[str, Any] = {
            "method": "order",
            "acctType": acct_type,
            "amount": amount,
            "currency": format_market(currency),
            "price": price,
            "tradeType": trade_type,
        }
        if order_type is not None:
            payload["orderType"] = order_type
        if customer_order_id is not None:
            payload["customerOrderId"] = customer_order_id

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "order",
            payload=payload,
        )

    async def order_morev2(
        self,
        market: str,
        trade_params: str,
        trade_type: int,
        acct_type: Optional[int] = 0,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "orderMoreV2",
            "market": market,
            "tradeParams": trade_params,
            "tradeType": trade_type,
            "acctType": acct_type,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "orderMoreV2",
            payload=payload,
        )

    async def cancel_order(
        self, currency: str, id: int, customer_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "cancelOrder",
            "currency": format_market(currency),
            "id": id,
        }

        if customer_order_id is not None:
            payload["customerOrderId"] = customer_order_id

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "cancelOrder",
            payload=payload,
        )

    async def get_order(
        self, id: int, currency: str, customer_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getOrder",
            "id": str(id),
            "currency": format_market(currency),
            "customerOrderId": customer_order_id,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getOrder",
            payload=payload,
        )

    async def get_orders(self, trade_type: int, currency: str, page_index: Optional[int] = None):
        payload: Dict[str, Any] = {
            "method": "getOrders",
            "tradeType": str(trade_type),
            "currency": format_market(currency),
        }

        if page_index is not None:
            payload["pageIndex"] = page_index

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getOrders",
            payload=payload,
        )

    async def get_orders_ignore_trade_type(
        self,
        currency: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getOrdersIgnoreTradeType",
            "currency": format_market(currency),
        }

        if page_index is not None:
            payload["pageIndex"] = str(page_index)
        if page_size is not None:
            payload["pageSize"] = str(page_size)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getOrdersIgnoreTradeType",
            payload=payload,
        )

    async def get_unfinished_orders_ignore_trade_type(
        self,
        currency: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getUnfinishedOrdersIgnoreTradeType",
            "currency": format_market(currency),
        }

        if page_index is not None:
            payload["pageIndex"] = str(page_index)
        if page_size is not None:
            payload["pageSize"] = str(page_size)

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getUnfinishedOrdersIgnoreTradeType",
            payload=payload,
        )

    async def get_finished_and_partial_orders(
        self,
        currency: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getFinishedAndPartialOrders",
            "currency": format_market(currency),
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getFinishedAndPartialOrders",
            payload=payload,
        )

    async def add_sub_user(self, memo: str, password: str, sub_user_name: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "memo": memo,
            "password": password,
            "subUserName": sub_user_name,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "addSubUser",
            payload=payload,
        )

    async def get_sub_user_list(self) -> Dict[str, Any]:
        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getSubUserList",
            payload=None,
        )

    async def do_transfer_funds(
        self, amount: float, currency: str, from_user_name: str, to_user_name: str
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "amount": amount,
            "currency": format_market(currency),
            "fromUserName": from_user_name,
            "toUserName": to_user_name,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "doTransferFunds",
            payload=payload,
        )

    async def get_lever_assets_info(self) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getLeverAssetsInfo",
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getLeverAssetsInfo",
            payload=payload,
        )

    async def get_lever_bills(
        self,
        coin: str,
        data_type: int,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getLeverBills",
            "coin": coin,
            "dataType": data_type,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getLeverBills",
            payload=payload,
        )

    async def transfer_in_lever(self, coin: str, market_name: str, amount: float) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "transferInLever",
            "coin": coin,
            "marketName": market_name,
            "amount": amount,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "transferInLever",
            payload=payload,
        )

    async def transfer_out_lever(
        self, coin: str, market_name: str, amount: float
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "transferOutLever",
            "coin": coin,
            "marketName": market_name,
            "amount": amount,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "transferOutLever",
            payload=payload,
        )

    async def loan(
        self,
        coin: str,
        amount: float,
        interest_rate_of_day: float,
        repayment_day: int,
        is_loop: bool,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "load",
            "coin": coin,
            "amount": amount,
            "interestRateOfDay": interest_rate_of_day,
            "repaymentDay": repayment_day,
            "isLoop": is_loop,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "loan",
            payload=payload,
        )

    async def cancel_loan(self, loan_id: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "cancelLoan",
            "loanId": loan_id,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "cancelLoan",
            payload=payload,
        )

    async def get_loans(
        self,
        coin: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getLoans",
            "coin": coin,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getLoans",
            payload=payload,
        )

    async def get_loan_records(
        self,
        market_name: str,
        status: int,
        loan_id: Optional[str] = "",
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getLoanRecords",
            "loanId": loan_id,
            "marketName": market_name,
            "status": status,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getLoanRecords",
            payload=payload,
        )

    async def borrow(
        self,
        market_name: str,
        coin: str,
        amount: float,
        interest_rate_of_day: float,
        repayment_day: int,
        is_loop: int,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "borrow",
            "marketName": market_name,
            "coin": coin,
            "amount": amount,
            "interestRateOfDay": str(interest_rate_of_day),
            "repaymentDay": str(repayment_day),
            "isLoop": is_loop,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "borrow",
            payload=payload,
        )

    async def auto_borrow(
        self,
        market_name: str,
        coin: str,
        amount: float,
        interest_rate_of_day: float,
        repayment_day: int,
        safe_pwd: str,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "autoBorrow",
            "marketName": market_name,
            "coin": coin,
            "amount": amount,
            "interestRateOfDay": interest_rate_of_day,
            "repaymentDay": repayment_day,
            "safePwd": safe_pwd,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "autoBorrow",
            payload=payload,
        )

    async def repay(
        self, loan_record_id: str, repay_amount: float, repay_type: int
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "repay",
            "loanRecordId": loan_record_id,
            "repayAmount": repay_amount,
            "repayType": repay_type,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "repay",
            payload=payload,
        )

    async def do_all_repay(self, market_name: str, coin: str, repay_amount: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "doAllRepay",
            "marketName": market_name,
            "coin": coin,
            "repayAmount": repay_amount,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "doAllRepay",
            payload=payload,
        )

    async def get_repayments(
        self,
        loan_record_id: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getRepayments",
            "loanRecordId": loan_record_id,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getRepayments",
            payload=payload,
        )

    async def get_finance_records(
        self,
        coin: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getFinanceRecords",
            "coin": coin,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getFinanceRecords",
            payload=payload,
        )

    async def change_invest_mark(self, invest_mark: int, loan_record_id: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "changeInvestMark",
            "investMark": invest_mark,
            "loanRecordId": loan_record_id,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "changeInvestMark",
            payload=payload,
        )

    async def change_loop(self, is_loop: int, loan_id: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "changeLoop",
            "isLoop": is_loop,
            "loanId": loan_id,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "changeLoop",
            payload=payload,
        )

    async def get_cross_assets(self) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "method": "getCrossAssets",
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getCrossAssets",
            payload=payload,
        )

    async def get_cross_bills(
        self,
        coin: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getCrossBills",
            "coin": coin,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getCrossBills",
            payload=payload,
        )

    async def transfer_in_cross(self, coin: str, amount: float) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "transferInCross",
            "coin": coin,
            "amount": amount,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "transferInCross",
            payload=payload,
        )

    async def transfer_out_cross(self, coin: str, amount: float) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "transferOutCross",
            "coin": coin,
            "amount": amount,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "transferOutCross",
            payload=payload,
        )

    async def do_cross_loan(self, coin: str, amount: float, safe_pwd: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "doCrossLoan",
            "coin": coin,
            "amount": amount,
            "safePwd": safe_pwd,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "doCrossLoan",
            payload=payload,
        )

    async def do_cross_repay(self, coin: str, repay_amount: float) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "doCrossRepay",
            "coin": coin,
            "repayAmount": repay_amount,
        }

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "doCrossRepay",
            payload=payload,
        )

    async def get_cross_repay_records(
        self,
        coin: str,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": "getCrossRepayRecords",
            "coin": coin,
        }

        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size

        return await self.client.sign_request(
            http_method="GET",
            url_path=self.BASE_ENDPOINT + "getCrossRepayRecords",
            payload=payload,
        )
