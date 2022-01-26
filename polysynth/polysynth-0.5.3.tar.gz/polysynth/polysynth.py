import os, sys
import time
from datetime import datetime
import logging
from typing import Any, Optional, Union, Dict

from web3 import Web3
from web3.eth import Contract
from web3.contract import ContractFunction
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.types import (
    TxParams,
    Wei,
    Nonce,
    HexBytes,
)
from polysynth.enum import ErrorMessage, PnlCalcOption, StatusCode

from polysynth.exception import InvalidParameterError, MissingInputError, PolysynthException, TransactionFailedError
from .types import AddressLike, FundingRateRes, MarginRes, OpenPositionRes, Response, TraderPosition
from .util import (
    _str_to_addr,
    _addr_to_str,
    _load_contract,
    _load_oracle_contract,
    _side_str_to_int,
    _amm_name_to_addr,
    _amm_name_to_oracle_addr,
    _int_to_bignum,
    _check_leverage,
    _check_slippage,
    _check_collateral,
    _normalize,
    _estimate_gas_fee
)

from .constants import (
    _netid_to_name,
    _contract_addresses_proxy_v1,
    _contract_addresses_oracle
)

logger = logging.getLogger(__name__)

class Polysynth:
    """
    Wrapper around Polysynth contract
    """

    def __init__(
        self,
        address: Union[AddressLike, str, None],
        private_key: Optional[str],
        provider: str = None,
        web3: Web3 = None,
        version: int = 1,
        default_slippage: float = 0.005,
        stable_token_contract_addr: str = None,
        manager_contract_addr: str = None,
        amm_reader_contract_addr: str= None
    ):
        """
        :param address: The public address of the account to use.
        :param private_key: The private key of the account to use.
        :param provider: Can be optionally set to a Web3 provider URI. If none set, will fall back to the PROVIDER environment variable, or web3 if set.
        :param web3: Can be optionally set to a custom Web3 instance.
        :param version: Which version of the Polysynth contract to use.
        :param default_slippage: Default slippage for a trade, as a float(0.01 is 1 %).
        """
        try:
            self.address: AddressLike = _str_to_addr(
                address or "0x0000000000000000000000000000000000000000"
                )
            self.private_key = (
                private_key
                or "0x0000000000000000000000000000000000000000000000000000000000000000"
                )
            self.version = version
            self.default_slippage = default_slippage

            if web3:
                self.w3 = web3
            else:
                self.provider = provider or os.environ["PROVIDER"]
                self.w3 = Web3(
                    Web3.HTTPProvider(self.provider, request_kwargs={"timeout": 60})
                    )
            
            # self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            # self.w3.transactionManager.UseLegacyAsDefault = True
            
            netid = 0
            try:
                netid = int(self.w3.net.version)
                if netid in _netid_to_name:
                    self.network = _netid_to_name[netid]
                else:
                    raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UNKNOWN_PROVIDER.value, ErrorMessage.INVALID_PROVIDER_URL.value)
            except:
                raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UNKNOWN_PROVIDER.value, ErrorMessage.INVALID_PROVIDER_URL.value)

            self.last_nonce: Nonce = self.w3.eth.get_transaction_count(self.address)

            self.max_approval_hex = f"0x{64 * 'f'}"
            self.max_approval_int = int(self.max_approval_hex, 16)
            self.max_approval_check_hex = f"0x{15 * '0'}{49 * 'f'}"
            self.max_approval_check_int = int(self.max_approval_check_hex, 16)

            self.fluctuation_limit = 0.012

            if self.version == 1:
                if stable_token_contract_addr is None:
                    stable_token_contract_addr = _contract_addresses_proxy_v1[self.network]["StableToken"]

                self.stable_token_addr = _str_to_addr(stable_token_contract_addr)
                self.stable_token_contract = _load_contract(
                    self.w3,
                    self.network,
                    abi_name="StableToken",
                    address=self.stable_token_addr,
                )

                if manager_contract_addr is None:
                    manager_contract_addr = _contract_addresses_proxy_v1[self.network]["Manager"]
        
                self.manager_contract = _load_contract(
                    self.w3,
                    self.network,
                    abi_name="Manager",
                    address=_str_to_addr(manager_contract_addr),
                )

                if amm_reader_contract_addr is None:
                    amm_reader_contract_addr = _contract_addresses_proxy_v1[self.network]["AmmReader"]

                self.amm_reader_contract = _load_contract(
                    self.w3,
                    self.network,
                    abi_name="AmmReader",
                    address=_str_to_addr(amm_reader_contract_addr),
                )

        except PolysynthException as pe:
            print(pe)
            sys.exit()

    def input_price(
        self,
        amm: str,
        side: str,
        quoteAssetAmount: int,
        ) -> Response:
        ''' 
            For a market, get equivalent base token amount against quoted token amount

        Args:
            amm (str): name of the market, eg; ETH
            side (int): direction of the quoted asset
            quoteAssetAmount (Wei): quoted asset amount

        Returns:
            Any: Base asset amount
        '''
        try:
            price = _normalize(self._input_price(amm, side, quoteAssetAmount)[0])
            return Response(StatusCode.OK.value, None, None, data= {"amount": abs(price) })
        except PolysynthException as e:
            return e
    
    def output_price(
        self,
        amm: str,
        side: str,
        baseAssetAmount: int,
        ) -> Response:
        ''' 
            For a market, get equivalent quoted token amount against base token amount

        Args:
            amm (str): name of the market, eg; ETH
            side (int): direction of the base asset
            baseAssetAmount (Wei): base asset amount

        Returns:
            Any: Quote asset amount
        '''
        try:
            amm_contract_addr = _amm_name_to_addr(amm, self.network)
            amm_contract = _load_contract(
                    self.w3,
                    self.network,
                    abi_name="Amm_" + amm.split("-")[0].upper(),
                    address=_str_to_addr(amm_contract_addr),
                )
            price = amm_contract.functions.getOutputPrice(
                _side_str_to_int(side),
                _int_to_bignum(baseAssetAmount)
            ).call()
            return Response(StatusCode.OK.value, None, None, data= { "amount": abs(_normalize(price[0])) })
        except PolysynthException as e:
            return e

    def open_position(
        self,
        amm: str,
        side: str,
        quoteAssetAmount: int,
        leverage: int,
        slippage: int = 0.005
    ) -> Response:
        ''' 
            Open trader's long/short position against an amm

        Args:
            amm (str): name of the market, eg; ETH
            side (int): direction of the trade; 0-buy, 1-sell
            quoteAssetAmount (Wei): quote asset amount
            leverage (int): leverage on quoted amount
            slippage (int): Slippage tolerance

        Returns:
            Hexbytes: Transaction Hash
        '''
        try:
            self.check_trade_constraints(amm, side, quoteAssetAmount, leverage, slippage)

            # set allowance for manager to spend token on behalf of user
            allowance = self.allowance()
            if allowance < self.max_approval_int/2:
                self.approve()

            _amm_contract_addr = _amm_name_to_addr(amm, self.network)
            _side = _side_str_to_int(side)
            _quote_asset_limit = self._quote_asset_limit(amm, quoteAssetAmount, leverage, _side, slippage)

            manager = self.manager_contract.functions
            tx_params = self._get_tx_params()
            func_params = [
                _amm_contract_addr,
                _side,
                _int_to_bignum(quoteAssetAmount),
                leverage,
                abs(int(_quote_asset_limit)),
            ]

            func = manager.openPosition(*func_params)
            receipt = self._build_and_send_tx(func, tx_params)
            tx = self.w3.eth.wait_for_transaction_receipt(receipt, timeout=1000)

            time.sleep(2)

            position = self._trader_position(amm)
            _price = round(position[2]/position[0], 4)
            _size = _normalize(position[0])
            _side = "BUY" if _size > 0 else "SELL"
            _leverage = round(position[2]/position[1], 4)

            _collateral_ratio = _normalize(self._collateral_ratio(amm))

            result = OpenPositionRes(_price, _side, _size, _leverage, _collateral_ratio, tx).__dict__()

            return Response(StatusCode.OK.value, None, None, data=result)
        except PolysynthException as e:
            return e

    def close_position(
        self,
        amm: str,
        slippage = 0.005
    ) -> Response:
        '''
            Close trader's position against an amm

        Args:
            amm (str): name of the market, eg; ETH
            slippage (int): Slippage tolerance

        Returns:
            Hexbytes: Transaction Hash
        '''
        try:
            _check_slippage(slippage)

            # check if no position open
            _position = self._trader_position(amm)
            _size = _normalize(_position[0])
            if _size == 0:
                raise TransactionFailedError(StatusCode.FAILED_TRASACTION.value, StatusCode.EXECUTION_REVERTED.value, ErrorMessage.NO_POSITIONS_OPEN.value)

            amm_contract_addr = _amm_name_to_addr(amm, self.network) # for eg resolves to Amm_eth

            _stable_asset_limit = self._stable_asset_limit(amm, slippage)

            manager = self.manager_contract.functions
            tx_params = self._get_tx_params()
            func_params = [
                amm_contract_addr,
                abs(int(_stable_asset_limit)),
            ]

            func = manager.closePosition(*func_params)
            receipt = self._build_and_send_tx(func, tx_params)
            tx = self.w3.eth.wait_for_transaction_receipt(receipt, timeout=1000)

            result = {
                "tx_hash": tx["transactionHash"].hex(),
                "gas_fees": tx["gasUsed"],
            }

            return Response(StatusCode.OK.value, None, None, data=result)
        except PolysynthException as e:
            return e
    
    def add_margin(
        self,
        amm: str,
        collateral: int
    ) -> Response:
        '''
            Add collateral to trader's account
        Args:
            amm (str): name of the market, eg; ETH
            collateral (int): Collateral Amount

        Returns:
            Hexbytes: Transaction Hash
        '''
        try:
            amm_contract_addr = _amm_name_to_addr(amm, self.network) # for eg resolves to Amm_eth
            manager = self.manager_contract.functions
            func_params = [
                amm_contract_addr,
                _int_to_bignum(collateral),
            ]

            tx_params = self._get_tx_params()
            func = manager.addCollateral(*func_params)
            receipt = self._build_and_send_tx(func, tx_params)
            tx = self.w3.eth.wait_for_transaction_receipt(receipt, timeout=1000)
            time.sleep(1)
            # get trader's new leverage and margin
            position = self._trader_position_with_funding_payment(amm)
            new_collateral, new_leverage = _normalize(position[1]), round(position[2]/position[1], 4)

            _unrealized_pnl = _normalize(self._unrealized_pnl(amm))
            _margin_after = new_collateral + _unrealized_pnl

            ratio = _normalize(self._collateral_ratio(amm))
            result = MarginRes(_margin_after, new_leverage, ratio, tx).__dict__()

            return Response(StatusCode.OK.value, None, None, data=result)
        except ContractLogicError as e:
            return TransactionFailedError(StatusCode.FAILED_TRASACTION.value, StatusCode.EXECUTION_REVERTED.value, ErrorMessage.NO_POSITIONS_OPEN.value)
        except PolysynthException as e:
            return e

    def remove_margin(
        self,
        amm: str,
        collateral: int
    ) -> Response:
        '''
            Remove collateral from trader's account
        Args:
            amm (str): name of the market, eg; ETH
            collateral (int): Collateral Amount

        Returns:
            Response Body
        '''
        try:
            amm_contract_addr = _amm_name_to_addr(amm, self.network) # for eg resolves to Amm_eth
            # check if value doesn't exceed trader's collateral
            _position_curr = self._trader_position_with_funding_payment(amm)
            _collateral = _normalize(_position_curr[1])
            _unrealized_pnl = _normalize(self._unrealized_pnl(amm))

            _margin_ratio_curr = _normalize(self._collateral_ratio(amm))
            _margin = _collateral + _unrealized_pnl

            _collateral_ratio_after = ( _margin - collateral ) / ( _margin/_margin_ratio_curr )

            if _collateral_ratio_after < 0.0625:
                raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.COLLATERAL_NOT_ENOUGH.value, ErrorMessage.COLLATERAL_NOT_ENOUGH.value)

            manager = self.manager_contract.functions
            func_params = [
                amm_contract_addr,
                _int_to_bignum(collateral),
            ]

            tx_params = self._get_tx_params()
            func = manager.removeCollateral(*func_params)
            receipt = self._build_and_send_tx(func, tx_params)
            tx = self.w3.eth.wait_for_transaction_receipt(receipt, timeout=1000)

            position = self._trader_position_with_funding_payment(amm)
            new_collateral, new_leverage = _normalize(position[1]), round(position[2]/position[1], 4)

            _unrealized_pnl = _normalize(self._unrealized_pnl(amm))
            _margin_after = new_collateral + _unrealized_pnl

            ratio = _normalize(self._collateral_ratio(amm))
            result = MarginRes(_margin_after, new_leverage, ratio, tx).__dict__()
            return Response(StatusCode.OK.value, None, None, data=result)
        except ContractLogicError as e:
            return TransactionFailedError(StatusCode.FAILED_TRASACTION.value, StatusCode.EXECUTION_REVERTED.value, ErrorMessage.NO_POSITIONS_OPEN.value)
        except PolysynthException as e:
            return e
 
    def allowance(
        self,
    ) -> Any:
        """Allowance"""
        token = self.stable_token_contract.functions
        scaled_amount = token.allowance(
            self.address,
            _contract_addresses_proxy_v1[self.network]["Manager"]
            ).call()
        return scaled_amount

    def approve(
        self,
    ) -> None:
        """Approve the amount"""
        token = self.stable_token_contract.functions
        func_params = [
            _contract_addresses_proxy_v1[self.network]["Manager"],
            self.max_approval_int,
        ]

        func = token.approve(*func_params)
        tx_params = self._get_tx_params()
        txid = self._build_and_send_tx(func, tx_params)
        self.w3.eth.wait_for_transaction_receipt(txid, timeout=6000)

        time.sleep(1)

    def mark_price(
        self,
        amm: str = None,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            For a market, get current spot price

        Args:
            amm (str): name of the market, eg; ETH

        Returns:
            Any: spot price
        '''
        try:
            price = _normalize(self._spot_price(amm))
            return Response(StatusCode.OK.value, None, None, data= {"mark_price": price })
        except PolysynthException as e:
            return e

    def fluctuation_limit_ratio(
        self,
        amm: str = None,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            For a market, get fluctuation limit ratio

        Args:
            amm (str): name of the market, eg; ETH

        Returns:
            Any: fluctuation limit ratio
        '''
        try:
            if amm is None:
                raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
            amm_contract_addr = _amm_name_to_addr(amm, self.network)
            amm_contract = _load_contract(
                    self.w3,
                    self.network,
                    abi_name="Amm_" + amm.split("-")[0].upper(),
                    address=_str_to_addr(amm_contract_addr),
                )
            flr = amm_contract.functions.fluctuationLimitRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"fluctuation_limit_ratio": round(flr/10**18, 7)})
        except PolysynthException as e:
            return e

    def trade_limit_ratio(
        self,
        amm: str = None,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            For a market, get trade limit ratio

        Args:
            amm (str): name of the market, eg; ETH

        Returns:
            Any: trade limit ratio
        '''
        try:
            if amm is None:
                raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
            amm_contract_addr = _amm_name_to_addr(amm, self.network)
            amm_contract = _load_contract(
                    self.w3,
                    self.network,
                    abi_name="Amm_" + amm.split("-")[0].upper(),
                    address=_str_to_addr(amm_contract_addr),
                )
            tlr = amm_contract.functions.tradeLimitRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"trade_limit_ratio": round(tlr/10**18, 7)})
        except PolysynthException as e:
            return e

    def margin_ratio(
        self,
        amm: str = None,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            For a market, get collateral ratio of the trader

        Args:
            amm (str): name of the market, eg; ETH

        Returns:
            Any: collateral ratio of the trader
        '''
        try:
            ratio = _normalize(self._collateral_ratio(amm))
            return Response(StatusCode.OK.value, None, None, data= {"margin_ratio": ratio})
        except ContractLogicError as e:
            return TransactionFailedError(StatusCode.FAILED_TRASACTION.value, StatusCode.EXECUTION_REVERTED.value, ErrorMessage.NO_POSITIONS_OPEN.value)
        except PolysynthException as e:
            return e

    def fee_ratio(
        self,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            Get fee ratio

        Args:

        Returns:
            Any: fee ratio
        '''
        try:
            fr = self.manager_contract.functions.feeRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"fee_ratio": round(fr/10**18, 7)})
        except PolysynthException as e:
            return e

    def init_margin_ratio(
        self,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            get init collateral ratio

        Args:

        Returns:
            Any: get initial collateral ratio
        '''
        try:
            icr = self.manager_contract.functions.initCollateralRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"init_margin_ratio": round(icr/10**18, 7)})
        except PolysynthException as e:
            return e

    def liquidation_fee_ratio(
        self,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            get liquidation fee ratio

        Args:

        Returns:
            Any: liquidation fee ratio
        '''
        try:
            lfr = self.manager_contract.functions.liquidationFeeRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"liquidation_fee_ratio": round(lfr/10**18, 7)})
        except PolysynthException as e:
            return e

    def maintenance_margin_ratio(
        self,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            get maintenance collateral ratio

        Args:

        Returns:
            Any: maintenance collateral ratio 
        '''
        try:
            mcr = self.manager_contract.functions.maintenanceCollateralRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"maintenance_margin_ratio": round(mcr/10**18, 7)})
        except PolysynthException as e:
            return e

    def partial_liquidation_ratio(
        self,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            get partial liquidation ratio

        Args:

        Returns:
            Any: partial liquidation ratio 
        '''
        try:
            plr = self.manager_contract.functions.partialLiquidationRatio().call()
            return Response(StatusCode.OK.value, None, None, data= {"partial_liquidation_ratio": round(plr/10**18, 7)})
        except PolysynthException as e:
            return e

    def price_impact(
        self,
        amm: str,
        size : int,
        **kwargs
        ) -> Response:
        '''
            get price impact
        Args:
            amm (str): name of the market, eg; ETH
            side (int): direction of the quoted asset
            quoteAssetAmount (int): quoted asset amount
            leverage (int): leverage on quote asset
        Returns:
            Any: fluctuation value 
        '''
        try:
            quoteAssetAmount = _normalize(self._output_price(amm, "BUY", size)[0])

            fluctuation = self._price_impact(amm, quoteAssetAmount, 1, 0)
            return Response(StatusCode.OK.value, None, None, data= {"price_impact": round(fluctuation, 7)})
        except PolysynthException as e:
            return e

    def wallet_balance(
        self,
        **kwargs
        ) -> Response:
        '''
            get wallet balance
        Args:
        Returns:
            Any: trader wallet balance
        '''
        try:
            balance = self._wallet_balance()
            return Response(StatusCode.OK.value, None, None, data= {"wallet_balance": round(balance/10**6, 7)})
        except PolysynthException as e:
            return e
    
    def unrealized_pnl(
        self,
        amm: str,
        **kwargs
        ) -> Response:
        '''
            Get unrealized pnl of a trader
        Args:
            amm: str
        Returns:
            Any: unrealized pnl of a trader
        '''
        try:
            unrealized_pnl = _normalize(self._unrealized_pnl(amm))
            return Response(StatusCode.OK.value, None, None, data= {"unrealized_pnl": unrealized_pnl})
        except PolysynthException as e:
            return e

    def positions(
        self,
        **kwargs
        ) -> Response:
        '''
            get price impact
        Args:
            amm (str): name of the market, eg; ETH
        Returns:
            Any: fluctuation value 
        '''
        try:
            res = []
            for key in _contract_addresses_proxy_v1[self.network].keys():
                if 'usdc' not in key: continue # filter all non-amm addresses

                amm = key.split('_')[1]
                position = self._trader_position(amm)
            
                size = _normalize(position[0])
                collateral = _normalize(position[1])

                if size == 0 or collateral == 0: continue

                leverage = round(position[2]/position[1], 4)
                avg_entry_price = round(position[2]/position[0], 4)

                position_with_funding_payment = self._trader_position_with_funding_payment(amm)
                unrealized_pnl = _normalize(self._unrealized_pnl(amm))

                margin = _normalize(position_with_funding_payment[1]) + unrealized_pnl # collateral + unrealized_pnl

                side = "BUY" if size > 0 else "SELL"

                result = TraderPosition(amm.upper(), side, size, collateral, leverage, avg_entry_price, margin, unrealized_pnl).__dict__()
                res.append(result)
            return Response(StatusCode.OK.value, None, None, data=res)
        except PolysynthException as e:
            return e

    def index_price(
        self,
        amm: str = None,
        *args,
        **kwargs
        ) -> Response:
        ''' 
            For a market, get oracle price from chainlink

        Args:
            amm (str): name of the market, eg; ETH

        Returns:
            Any: oracle price from chainlink
        '''
        try:
            if amm is None:
                raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
            oracle_addr = _amm_name_to_oracle_addr(amm, self.network)
            oracle_contract = _load_oracle_contract(
                    self.w3,
                    address=_str_to_addr(oracle_addr),
                )
            price = oracle_contract.functions.latestRoundData().call()
            return Response(StatusCode.OK.value, None, None, data= {"index_price": round(price[1]/10**8, 4)})
        except PolysynthException as e:
            return e

    def funding_rate(
        self,
        amm: str,
        *args,
        **kwargs
        ) -> Response:
        '''
            For a given market, get all the funding rates
        Args:
            amm (str): name of the market, eg; ETH-USDC
        Returns: 
        Any: funding rates (long/short)
        '''
        try:
            if amm is None:
                raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

            amm_contract_addr = _amm_name_to_addr(amm, self.network)

            amm_reader = self.amm_reader_contract.functions
            amm_metadata = amm_reader.getAmmMetadata(amm_contract_addr).call()
            
            funding_rate_long, funding_rate_short = round(amm_metadata[4]/10**18, 7), round(amm_metadata[5]/10**18, 7)

            futures = amm.upper()
            result = FundingRateRes(funding_rate_long, funding_rate_short, futures).__dict__()
            return Response(StatusCode.OK.value, None, None, data= result)
        except PolysynthException as e:
            return e

    def check_trade_constraints(self, amm: str, dir: str, quoteAssetAmount: int, leverage: int, slippage: int) -> Any:
        try:
            _side = _side_str_to_int(dir)
            _check_collateral(quoteAssetAmount)
            _check_leverage(leverage)
            _check_slippage(slippage)
            
            # check wallet balance
            self._check_wallet(quoteAssetAmount, leverage)
            # check price impact
            self._check_fluctuation(amm, quoteAssetAmount, leverage, _side)
        except TypeError:
            invalid_args = ""
            if not isinstance(amm, str): invalid_args += "market"
            if not isinstance(quoteAssetAmount, int): invalid_args += " quoteAssetAmount"
            if not isinstance(leverage, int): invalid_args += " leverage"
            if not( isinstance(slippage, int) or isinstance(slippage, float)): invalid_args += " slippage"

            raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.INVALID_ARG_TYPE.value, ErrorMessage.INVALID_ARG_TYPE.value%(invalid_args+" "))
    
    def _input_price(self, amm: str, side: int, quoteAssetAmount: int) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_contract = _load_contract(
            self.w3,
            self.network,
            abi_name="Amm_" + amm.split("-")[0].upper(),
            address=_str_to_addr(amm_contract_addr),
            )
        price = amm_contract.functions.getInputPrice(
            _side_str_to_int(side),
            _int_to_bignum(quoteAssetAmount)
            ).call()
        return price
    
    def _output_price(self, amm: str, side: int, baseAssetAmount: int) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_contract = _load_contract(
            self.w3,
            self.network,
            abi_name="Amm_" + amm.split("-")[0].upper(),
            address=_str_to_addr(amm_contract_addr),
            )
        price = amm_contract.functions.getOutputPrice(
            _side_str_to_int(side),
            _int_to_bignum(baseAssetAmount)
            ).call()
        return price

    def _spot_price(self, amm, **kwargs) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_contract = _load_contract(
            self.w3,
            self.network,
            abi_name="Amm_" + amm.split("-")[0].upper(),
            address=_str_to_addr(amm_contract_addr),
        )
        price = amm_contract.functions.getSpotPrice().call()
        return price
    
    def _quote_asset_limit(self, amm: str, quoteAssetAmount: int, leverage: int, side: int, slippage: int) -> Any:
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        notional = int(quoteAssetAmount * leverage * 10**18)

        amm_reader = self.amm_reader_contract.functions
        reserve = amm_reader.getBaseAssetAmount(amm_contract_addr, side, notional).call()

        _positionSize = reserve[0]
        quoteAssetLimit = None

        if slippage == 0:
            quoteAssetLimit = _positionSize
        else:
            quoteAssetLimit =  _positionSize * (1-slippage) if side == 0 else _positionSize * (1+slippage)

        return quoteAssetLimit
    
    def _stable_asset_limit(self, amm: str, slippage: int) -> Any:
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_reader = self.amm_reader_contract.functions

        # size owned by trader
        _size = self._trader_position(amm)[0]

        _side = 0 if _size > 0 else 1

        _sold_token = amm_reader.getStableTokenAmount(amm_contract_addr, _side, abs(_size)).call()[0]

        _stable_token_limit = _sold_token*(1 - slippage) if _size > 0 else _sold_token*(1 + slippage)

        return _stable_token_limit

    def _trader_position(self, amm: str) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_reader = self.amm_reader_contract.functions

        position = amm_reader.getTraderPosition(amm_contract_addr, self.address).call()
        return position
    
    def _trader_position_with_funding_payment(self, amm: str) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_reader = self.amm_reader_contract.functions

        position = amm_reader.getTraderPositionWithFundingPayment(amm_contract_addr, self.address).call()
        return position
    
    def _unrealized_pnl(self, amm: str) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)

        position = self.manager_contract.functions.getPositionNotionalAndUnrealizedPnl(
            amm_contract_addr,
            self.address,
            PnlCalcOption.SPOT_PRICE.value).call()
        
        unrealized_pnl = position[1]
        return unrealized_pnl

    def _get_data_for_jayant(self, amm: str, trader: str, id='latest') -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

        position = self._get_trader_position(amm, trader, id=id)

        _size = _normalize(position[0])
        _collateral = _normalize(position[1]) # 1

        if position[1] == 0 or position[0] == 0:
            _leverage = 0
            _avg_entry_price = 0
        else:
            _leverage = '{:.20f}'.format((position[2]/position[1]))
            _avg_entry_price = '{:.20f}'.format((position[2]/position[0])) #3

        _position_with_funding_payment = self._get_trader_position_with_funding_payment(amm, trader,id=id)

        _collateral_with_funding_rate = _normalize(_position_with_funding_payment[1])
        _funding_rate_long = _normalize(_position_with_funding_payment[4])
        _funding_rate_short = _normalize(_position_with_funding_payment[5])

        _with_spot = self._get_position_notional_and_unrealized_pnl(amm, trader, id=id, option=0)
        _with_twap = self._get_position_notional_and_unrealized_pnl(amm, trader, id=id, option=1)

        _position_notional_spot = _normalize(_with_spot[0])
        _position_notional_twap = _normalize(_with_twap[0]) #4

        _unrealized_pnl_spot = _normalize(_with_spot[1])
        _unrealized_pnl_twap = _normalize(_with_twap[1])

        _margin = _normalize(_position_with_funding_payment[1] + _with_spot[1]) #2

        _spot_price = _normalize(self._get_spot_price(amm, id=id))

        _collateral_ratio =  _normalize(self._get_collateral_ratio(amm, trader, id=id))

        return {
            "amm": amm,
            "trader": trader,
            "collateral": _collateral,
            "size": _size,
            "leverage": _leverage,
            "entry_price": _avg_entry_price,
            "collateral_with_funding_rate": _collateral_with_funding_rate,
            "funding_rate_long": _funding_rate_long,
            "funding_rate_short": _funding_rate_short,
            "position_notional_spot": _position_notional_spot,
            "position_notional_twap": _position_notional_twap,
            "unrealized_pnl_spot": _unrealized_pnl_spot,
            "unrealized_pnl_twap": _unrealized_pnl_twap,
            "margin": _margin,
            "spot_price": _spot_price,
            "collateral_ratio": _collateral_ratio
        }
    
    def _get_spot_price(self, amm: str, id='latest', **kwargs) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_contract = _load_contract(
            self.w3,
            self.network,
            abi_name="Amm_" + amm.split("-")[0].upper(),
            address=_str_to_addr(amm_contract_addr),
        )
        price = amm_contract.functions.getSpotPrice().call(block_identifier=id)
        return price

    def _get_trader_position_with_funding_payment(self, amm: str, trader: str, id='latest') -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_reader = self.amm_reader_contract.functions

        position = amm_reader.getTraderPositionWithFundingPayment(amm_contract_addr, trader).call(block_identifier=id)
        return position

    def _get_trader_position(self, amm: str, trader: str, id='latest') -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_reader = self.amm_reader_contract.functions

        position = amm_reader.getTraderPosition(amm_contract_addr, trader).call(block_identifier=id)
        return position
    
    def _get_position_notional_and_unrealized_pnl(self, amm: str, trader: str, id='latest', option=0) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)

        position = self.manager_contract.functions.getPositionNotionalAndUnrealizedPnl(
            amm_contract_addr,
            trader,
            option).call(block_identifier=id)
        
        return position
    
    def _get_collateral_with_funding_payment(self, amm, trader, id='latest', **kwargs) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")
        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        amm_contract = _load_contract(
            self.w3,
            abi_name="Amm_" + amm.split("-")[0].upper(),
            address=_str_to_addr(amm_contract_addr),
        )

        position = self._get_trader_position(amm, trader, id=id)

        _spot = self._get_position_notional_and_unrealized_pnl(amm, trader, id=id, option=0)
        _twap = self._get_position_notional_and_unrealized_pnl(amm, trader, id=id, option=1)

        res =  _spot if _spot[1] > _twap[1]  else _twap

        price = amm_contract.functions.getCollateralWithFundingPayment(position, res[1]).call(block_identifier=id)
        return price
    
    def _get_collateral_ratio(self, amm: str, trader: str, id='latest') -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        try:
            ratio = self.manager_contract.functions.getCollateralRatio(amm_contract_addr, trader).call(block_identifier=id)
            return ratio
        except:
            return 0

    def _collateral_ratio(self, amm: str) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

        amm_contract_addr = _amm_name_to_addr(amm, self.network)
        ratio = self.manager_contract.functions.getCollateralRatio(amm_contract_addr, self.address).call()
        return ratio
    
    def _price_impact(self, amm: str, quoteAssetAmount: int, leverage: int, side: int) -> Any:
        if amm is None:
            raise MissingInputError(StatusCode.BAD_REQUEST.value, StatusCode.MISSING_REQUIRED_ARGS.value, ErrorMessage.MISSING_REQUIRED_ARGS.value%"symbol")

        _amm_contract_addr = _amm_name_to_addr(amm, self.network)
        _notional = int(quoteAssetAmount * leverage * 10**18)

        amm_reader = self.amm_reader_contract.functions

        reserve = amm_reader.getBaseAssetAmount(_amm_contract_addr, side, _notional).call()

        _base_reserve, _quote_reserve = reserve[1], reserve[2]
        _new_price = _quote_reserve/_base_reserve
        
        _curr_price = _normalize(self._spot_price(amm))

        fluctuation = abs(_curr_price - _new_price)/_curr_price

        return fluctuation

    def _check_fluctuation(self, amm: str, quoteAssetAmount: int, leverage: int, side: int) -> Any:
        fluctuation = self._price_impact(amm, quoteAssetAmount, leverage, side)
        if fluctuation > self.fluctuation_limit:
            raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.FLUCTUATION_LIMIT_EXCEEDED.value, ErrorMessage.FLUCTUATION_LIMIT_EXCEEDED.value%fluctuation)
        else:
            pass

    def _wallet_balance(self, **kwargs):
        stable_token = self.stable_token_contract.functions
        balance = stable_token.balanceOf(self.address).call()
        return balance
    
    def _check_wallet(self, quoteAssetAmount: int, leverage: int) -> Any:
        # check wallet balance
        balance = self._wallet_balance()/10**6

        # fees = 0.07 % of notional
        fees = 0.07 * (quoteAssetAmount * leverage)/100
        total_amount = quoteAssetAmount + fees

        if ( total_amount > balance):
            raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.INSUFFICIENT_WALLET_BALANCE.value, ErrorMessage.INSUFFICIENT_WALLET_BALANCE.value %(balance, total_amount))
        else:
            pass
    
    def mint_token(self):
        stable_token = self.stable_token_contract.functions

        tx_params = self._get_tx_params()
        func = stable_token.mintFake()
        receipt = self._build_and_send_tx(func, tx_params)
        tx = self.w3.eth.wait_for_transaction_receipt(receipt, timeout=1000)
        time.sleep(1)        
    
    def _build_and_send_tx(
        self, function: ContractFunction, tx_params: Optional[TxParams] = None
    ) -> HexBytes:
        """Build and send a transaction."""
        if not tx_params:
            tx_params = self._get_tx_params()
        transaction = function.buildTransaction(tx_params)
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        try:
            return self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        finally:
            logger.debug(f"nonce: {tx_params['nonce']}")
            self.last_nonce = Nonce(tx_params["nonce"] + 1)

    def _get_tx_params(self, value: Wei = Wei(0), gas: Wei = Wei(5000000)) -> TxParams:
        """Get generic transaction parameters."""
        gasFee = _estimate_gas_fee("standard", self.network)
        return {
            "from": _addr_to_str(self.address),
            "value": value,
            "maxFeePerGas": Web3.toWei(gasFee['maxFee'], 'gwei'),
            'maxPriorityFeePerGas': Web3.toWei(gasFee['maxPriorityFee'], 'gwei'),
            "nonce": max(
                self.last_nonce, self.w3.eth.get_transaction_count(self.address)
            ),
            "chainId": int(self.w3.net.version),
        }
