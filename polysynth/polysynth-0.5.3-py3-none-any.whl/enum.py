from enum import Enum, unique

@unique
class StatusCode(Enum):
    """ Status Code Enum.

    Example usage:
        StatusCode.OK.value #100
        StatusCode.INTERNAL_SERVER_ERROR.value #500
    """

    # SUCCESSFUL RESPONSES (100-199)
    OK = 200 # Success!

    # ERROR RESPONSES (400-499)
    BAD_REQUEST = 400
    
    REQUEST_TIMEOUT = 408
    TOO_MANY_REQUESTS = 429

    # contract execution (500-599)
    FAILED_TRASACTION = 500

    MISSING_REQUIRED_ARGS = 3000
    INVALID_ARG_TYPE = 3001
    EXECUTION_REVERTED = 3002
    UNKNOWN_PROVIDER = 3003
    UKNOWN_ADDRESS = 3004
    UNKNOWN_SIDE = 3005
    UNKNOWN_AMOUNT = 3006

    INVALID_LEVERAGE = 3007
    INVALID_SLIPPAGE = 3008
    FLUCTUATION_LIMIT_EXCEEDED = 3009
    INSUFFICIENT_WALLET_BALANCE = 3010
    ZERO_COLLATERAL = 3011
    COLLATERAL_NOT_ENOUGH = 3012
    

    
@unique
class ErrorMessage(Enum):
    """ Error Message Enum.

    Example usage:
        ErrorMessage.INVALID_PROVIDER.value # the privided rpc is not valid
        ErrorMessage.SLIPPAGE_LIMIT_EXCEEDED.value # the slippage should be between 0 to 0.05
    """
    # argument type/format related
    INVALID_ADDRESS_FORMAT = "Invalid address format provided"
    INVALID_PRIVATE_KEY = "Invalid private key provided"
    INVALID_PROVIDER_URL = "Unsupported network RPC Provided"
    INVALID_AMOUNT = "Invalid amount provided provided"

    ZERO_COLLATERAL = "Collateral cannot be zero"
    
    INVALID_LEVERAGE_VALUE = "Leverage only supportes integer values in range 1-10"

    INVALID_SIDE = "Invalid side provided: %s, expected BUY or SELL"
    INVALID_MARKET = "Invalid market name provided: %s"
    
    VERSION_NOT_SUPPORTED = "Provided version is not supported, set version to 1"

    SLIPPAGE_LIMIT_EXCEEDED = "Slippage should be in range 0 to 0.05"
    FLUCTUATION_LIMIT_EXCEEDED = "Fluctuation should be less than 0.012, but got %.4f"
    COLLATERAL_NOT_ENOUGH = "Margin ratio is below 6.25%, your position maybe liquidated. Please increase the value."
    
    MISSING_REQUIRED_ARGS = "Missing required arguments : [%s]"
    INVALID_KEYWORD_ARGS = "Invalid keyword arguments: [%s]"
    INVALID_ARG_TYPE = "Invalid argument type provided: [%s]"

    INSUFFICIENT_WALLET_BALANCE = "Wallet balance (%f) is less than trading amount (%f)"
    INSUFFICIENT_MATIC_BALANCE = "Unable to make transaction due to less matic balance"

    LOW_GAS_FEES = "Unable to make transaction due to low gas fee (%f)"

    # blockchain related error messages
    RPC_CONNECTION_ERROR = "Unable to establish connection to network"
    RPC_TIMED_OUT = "Unable to connect to a rpc node due to slow network connection"
    CANNOT_HANDLE_RPC_REQUEST = "The current provider is not able to handle rpc request."
    STALE_BLOCKCHAIN = "Stale block receieved"

    # contract related
    TRANSACTION_REVERT_ERROR = "Transaction reverted in contract"
    EXECUTION_REVERT_ERROR = "Execution reverted in contract"
    TRANSACTION_FAILED_ERROR = "Transaction failed in contract"

    NO_POSITIONS_OPEN = "No positions open currently"

@unique
class PnlCalcOption(Enum):
    SPOT_PRICE = 0
    TWAP = 1
    ORACLE = 2
