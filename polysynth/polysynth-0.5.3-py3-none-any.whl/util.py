import os
import json
import functools
from typing import Any, Union, List, Tuple
import requests

from web3 import Web3
from web3.exceptions import NameNotFound
from polysynth.enum import ErrorMessage, StatusCode

from polysynth.exception import InvalidFormatError, InvalidParameterError

from .types import AddressLike, Address, Contract
from .constants import (
    _contract_addresses_proxy_v1,
    _contract_addresses_oracle
)

def _str_to_addr(s: Union[AddressLike, str]) -> Address:
    """Idempotent"""
    try:
        if isinstance(s, str):
            if s.startswith("0x"):
                return Address(bytes.fromhex(s[2:]))
    except:
        raise InvalidFormatError(
            StatusCode.BAD_REQUEST.value, 
            StatusCode.UKNOWN_ADDRESS.value, 
            ErrorMessage.INVALID_ADDRESS_FORMAT.value)


def _addr_to_str(a: AddressLike) -> str:
    if isinstance(a, bytes):
        # Address or ChecksumAddress
        addr: str = Web3.toChecksumAddress("0x" + bytes(a).hex())
        return addr
    elif isinstance(a, str) and a.startswith("0x"):
        addr = Web3.toChecksumAddress(a)
        return addr

    raise InvalidFormatError(
                StatusCode.BAD_REQUEST.value, 
                StatusCode.UKNOWN_ADDRESS.value, 
                ErrorMessage.INVALID_ADDRESS_FORMAT.value)


def is_same_address(a1: Union[AddressLike, str], a2: Union[AddressLike, str]) -> bool:
    return _str_to_addr(a1) == _str_to_addr(a2)


def _validate_address(a: AddressLike) -> None:
    assert _addr_to_str(a)


def _load_abi(name: str, network: str) -> str:
    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + network + f".json")) as f:
        meta = json.load(f)
        abi = meta["contracts"][name]["abi"]
    return abi

def _load_oracle_abi() -> str:
    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + f"AggregatorV3InterfaceABI.json")) as f:
        meta = json.load(f)
        abi = meta["abi"]
    return abi


@functools.lru_cache()
def _load_contract(w3: Web3,  network: str, abi_name: str, address: AddressLike) -> Contract:
    address = Web3.toChecksumAddress(address)
    return w3.eth.contract(address=address, abi=_load_abi(abi_name, network))

@functools.lru_cache()
def _load_oracle_contract(w3: Web3, address: AddressLike) -> Contract:
    address = Web3.toChecksumAddress(address)
    return w3.eth.contract(address=address, abi=_load_oracle_abi())


def _load_contract_erc20(w3: Web3, address: AddressLike) -> Contract:
    return _load_contract(w3, "erc20", address)

def _side_str_to_int(side: str) -> Any:
    try:
        if side.lower() == 'buy':
            return 0
        elif side.lower() == 'sell':
            return 1
        else:
            raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UNKNOWN_SIDE.value, ErrorMessage.INVALID_SIDE.value %side)
    except:
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UNKNOWN_SIDE.value, ErrorMessage.INVALID_SIDE.value %side)

def _amm_name_to_addr(amm: str, network: str) -> Any:
    try:
        amm_title = "Amm_" + amm.lower()
        return _contract_addresses_proxy_v1[network][amm_title]
    except:
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UKNOWN_ADDRESS.value, ErrorMessage.INVALID_MARKET.value %amm)

def _amm_name_to_oracle_addr(amm: str, network: str) -> Any:
    try:
        amm_title = amm.lower()
        return _contract_addresses_oracle[network][amm_title]
    except:
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UKNOWN_ADDRESS.value, ErrorMessage.INVALID_MARKET.value %amm)

def _int_to_bignum(num):
    if isinstance(num, int) or isinstance(num, float):
        return int(num*(10**18))
    else:
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.UNKNOWN_AMOUNT.value, ErrorMessage.INVALID_AMOUNT.value)

def _check_leverage(leverage: int):
    if (leverage < 1 or leverage > 10) or (not isinstance(leverage, int)) or (not leverage % 1 == 0):
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.INVALID_LEVERAGE.value, ErrorMessage.INVALID_LEVERAGE_VALUE.value)
    else:
        pass

def _check_slippage(slippage):
    if not (isinstance(slippage, int) or isinstance(slippage, float)):
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.INVALID_SLIPPAGE.value, ErrorMessage.INVALID_ARG_TYPE.value%"slippage")
    if (slippage < 0 or slippage > 0.05):
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.INVALID_SLIPPAGE.value, ErrorMessage.SLIPPAGE_LIMIT_EXCEEDED.value)
    else:
        pass

def _check_collateral(quoteAssetAmount: int):
    if quoteAssetAmount == 0:
        raise InvalidParameterError(StatusCode.BAD_REQUEST.value, StatusCode.ZERO_COLLATERAL.value, ErrorMessage.ZERO_COLLATERAL.value)
    else:
        pass

def _normalize(amount: int):
    return round(amount/10**18, 7)

def _estimate_gas_fee(_type: str, _network: str):
    _url = None
    if _network == "matic":
        _url = "https://gasstation-mainnet.matic.network/v2"
    elif _network == "mumbai":
        _url = 'https://gasstation-mumbai.matic.today/v2'
    res = requests.get(_url).json()

    return res[_type]

