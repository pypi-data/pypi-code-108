import threading
from collections import namedtuple
from datetime import datetime


class AsyncWaiter(object):
    def __init__(self):
        self.WaiterEvent = threading.Event()
        self.Message = None


class FastReadCounter(object):
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.value += 1
            return str(self.value)


class SymbolType:
    Stock = 'Stock'
    FuturesStock = 'FuturesStock'
    OptionsStock = 'OptionsStock'
    FuturesIndex = 'FuturesIndex'
    OptionsIndex = 'OptionsIndex'
    Index = 'Index'


class OptionType:
    Unspecified = 'None'
    PE = 'PE'
    CE = 'CE'
    XX = 'XX'


class SlippageType:
    BPS = 'BPS'
    TIME = 'TIME'


class LogLevel:
    Debug = 'Debug'
    Error = 'Error'
    Information = 'Information'
    Warning = 'Warning'


class FNOPeriodType:
    Monthly = 'Monthly'
    Weekly = 'Weekly'


class TradeSymbol(object):
    def __init__(self,
                 symboltype=None,
                 ticker=None,
                 fno_period_type=FNOPeriodType.Monthly,
                 fno_month=0,
                 fno_week=0,
                 option_type=OptionType.Unspecified,
                 option_value=0,
                 script_token=0,
                 expiry_date=datetime(1, 1, 1),
                 **kwargs):
        if symboltype is None:
            fill_obj(self, **kwargs)
        else:
            self.SymbolType = symboltype
            self.Ticker = ticker
            self.FNOPeriodType = fno_period_type
            self.FNOMonth = fno_month
            self.FNOWeek = fno_week
            self.OptionType = option_type
            self.OptionValue = option_value
            self.ScripToken = 0
            self.ExpiryDate = expiry_date


def is_symbol_equal(source: TradeSymbol, target: TradeSymbol) -> bool:
    return source.Ticker == target.Ticker and \
           source.SymbolType == target.SymbolType and \
           source.OptionType == target.OptionType and \
           source.OptionValue == target.OptionValue and \
           source.FNOPeriodType == target.FNOPeriodType and \
           source.FNOMonth == target.FNOMonth and \
           source.FNOWeek == target.FNOWeek and \
           source.ExpiryDate == target.ExpiryDate


class TickData(object):
    def __init__(self, symbol=None, date=None, timestamp=None, ltp=None, ltq=None,
                 bid=None, ask=None, last_tick=None, open_interest=None, **kwargs):
        if symbol is None:
            fill_obj(self, **kwargs)
        else:
            self.Symbol = symbol
            self.Date = date
            self.Timestamp = timestamp
            self.LTP = ltp
            self.LTQ = ltq
            self.Bid = bid
            self.Ask = ask
            self.LastTick = last_tick
            self.OpenInterest = open_interest


class AlgorumMessageType:
    Request = 'Request'
    Response = 'Response'
    Oneway = 'Oneway'
    ErrorResponse = 'ErrorResponse'


class AlgorumWebsocketError(object):
    def __init__(self):
        self.ErrorCode: int
        self.ErrorMessage: str
        self.ErrorStackTrace: str


class QuantData(object):
    def __init__(self, key=None, value=None, **kwargs):
        if key is None:
            fill_obj(self, **kwargs)
        else:
            self.Key = key
            self.Value = value


class AlgorumWebsocketMessage(object):
    def __init__(self, name=None, message_type=None, cor_id=None, json_data=None, error=None, **kwargs):
        if name is None:
            fill_obj(self, **kwargs)
        else:
            self.Name = name
            self.MessageType: AlgorumMessageType = message_type
            self.CorId = cor_id
            self.JsonData = json_data
            self.Error: AlgorumWebsocketError = error


class AlgorumException(BaseException):
    def __init__(self, msg: AlgorumWebsocketMessage):
        self.Message = msg


class BacktestRequest(object):
    def __init__(self,
                 start_date: datetime,
                 end_date: datetime,
                 uid: str,
                 apikey: str,
                 api_secret_key: str,
                 client_code: str,
                 password: str,
                 two_factor_auth: str,
                 sampling_time_in_seconds: int,
                 brokerage_platform: str,
                 capital: float):
        self.StartDate = start_date
        self.EndDate = end_date
        self.Uid = uid
        self.ApiKey = apikey
        self.ApiSecretKey = api_secret_key
        self.ClientCode = client_code
        self.Password = password
        self.TwoFactorAuth = two_factor_auth
        self.SamplingTimeInSeconds = sampling_time_in_seconds
        self.BrokeragePlatform = brokerage_platform
        self.Capital = capital


class TradingRequest(object):
    def __init__(self,
                 apikey: str,
                 api_secret_key: str,
                 client_code: str,
                 password: str,
                 two_factor_auth: str,
                 sampling_time_in_seconds: int,
                 brokerage_platform: str,
                 capital: float):
        self.ApiKey = apikey
        self.ApiSecretKey = api_secret_key
        self.ClientCode = client_code
        self.Password = password
        self.TwoFactorAuth = two_factor_auth
        self.SamplingTimeInSeconds = sampling_time_in_seconds
        self.BrokeragePlatform = brokerage_platform
        self.Capital = capital


class StrategyLaunchMode:
    Backtesting = 'Backtesting'
    PaperTrading = 'PaperTrading'
    LiveTrading = 'LiveTrading'


class CandlePeriod:
    Second = 'Second'
    Minute = 'Minute'
    Day = 'Day'


class CreateIndicatorRequest(object):
    def __init__(self, symbol: TradeSymbol, candle_period: CandlePeriod, period_span: int):
        self.Symbol = symbol
        self.CandlePeriod = candle_period
        self.PeriodSpan = period_span


class IndicatorRequest(object):
    def __init__(self, indicator: str, param_map):
        self.Indicator = indicator
        self.ParamMap = param_map


class GetIndicatorsRequest(object):
    def __init__(self, indicator_uid: str, indicator_requests):
        self.IndicatorUid = indicator_uid
        self.IndicatorRequests = indicator_requests


class PreloadCandlesRequest(object):
    def __init__(self, uid: str, candle_count: int, preload_end_time: datetime, api_key: str,
                 api_secret_key: str):
        self.IndicatorUid = uid
        self.CandleCount = candle_count
        self.PreloadEndTime = preload_end_time
        self.ApiKey = api_key
        self.ApiSecretKey = api_secret_key


class OrderProductType:
    Normal = 'Normal'
    Intraday = 'Intraday'
    CashAndCarry = 'CashAndCarry'


class OrderType:
    Market = 'Market'
    Limit = 'Limit'


class OrderDirection:
    Buy = 'Buy'
    Sell = 'Sell'


class TradeExchange:
    NSE = 'NSE'
    BSE = 'BSE'
    NFO = 'NFO'
    PAPER = 'PAPER'


class BrokeragePlatform:
    NorthEast = 'NorthEast'
    Alpaca = 'Alpaca'


class OrderStatus:
    Pending = 'Pending'
    Completed = 'Completed'
    Cancelled = 'Cancelled'
    Rejected = 'Rejected'


class OptionsData(object):
    def __init__(self, **kwargs):
        self.Symbol: TradeSymbol
        self.LastTradeTime: datetime
        self.ServerTime: datetime
        self.LTP: float
        self.Bid: float
        self.Ask: float
        self.OpenInterest: float
        self.OpenInterestChange: float

        fill_obj(self, **kwargs)


class OptionsGreeks(object):
    def __init__(self, **kwargs):
        self.Symbol: TradeSymbol = TradeSymbol()
        self.Delta: float = 0.0
        self.Theta: float = 0.0
        self.Gamma: float = 0.0
        self.Vega: float = 0.0
        self.IV: float = 0.0
        self.IVVWap: float = 0.0
        self.Vanna: float = 0.0
        self.Charm: float = 0.0
        self.Speed: float = 0.0
        self.Zomma: float = 0.0
        self.Color: float = 0.0
        self.Volga: float = 0.0
        self.Veta: float = 0.0
        self.ThetaGammaRatio: float = 0.0
        self.ThetaVegaRatio: float = 0.0
        self.DTR: float = 0.0

        fill_obj(self, **kwargs)


class PlaceOrderRequest(object):
    def __init__(self):
        self.Symbol = None
        self.Timestamp: datetime = datetime.utcnow()
        self.Validity = None
        self.TradeExchange = TradeExchange.PAPER
        self.OrderType = OrderType.Market
        self.OrderDirection = OrderDirection.Buy
        self.OrderProductType = OrderProductType.Normal
        self.Tag = None
        self.Quantity: float = 0.0
        self.Price: float = 0.0
        self.TriggerPrice: float = 0.0
        self.SlippageType = SlippageType.BPS
        self.Slippage = 0.0
        self.ValidTillTime: datetime = datetime.utcnow()


def fill_obj(obj, **kwargs):
    for a in kwargs:
        if type(kwargs[a]) is dict:
            obj_inner = namedtuple(a, kwargs[a].keys())(*kwargs[a].values())
            setattr(obj, a, obj_inner)
        else:
            setattr(obj, a, kwargs[a])


class Order(object):
    def __init__(self, **kwargs):
        self.TriggerPrice: float = 0.0
        self.OrderDirection = None
        self.Symbol: TradeSymbol = TradeSymbol()
        self.Tag = None
        self.StatusMessage = None
        self.Status = None
        self.Quantity: float = 0.0
        self.Product = None
        self.Price: float = 0.0
        self.PlacedBy = None
        self.PendingQuantity: float = 0.0
        self.ParentOrderId = None
        self.OrderType = None
        self.OrderTimestamp: datetime = datetime.utcnow()
        self.OrderId = None
        self.InstrumentToken: int = 0
        self.FilledQuantity: float = 0.0
        self.ExchangeTimestamp: datetime = datetime.utcnow()
        self.ExchangeOrderId = None
        self.Exchange = None
        self.DisclosedQuantity: float = 0.0
        self.CancelledQuantity: float = 0.0
        self.AveragePrice: float = 0.0
        self.Validity = None
        self.Variety = None
        self.BrokerageOrderJson = None
        self.LastTick: TickData = TickData()
        self.SlippageType = None
        self.Slippage = 0.0
        self.RunId = None
        self.ValidTillTime: datetime = datetime.utcnow()

        fill_obj(self, **kwargs)


class CrossAbove(object):
    def __init__(self):
        self.StopCrossOverUpdate = True
        self.CrossOverReached = False

    def evaluate(self, left_val: float, right_val: float) -> bool:
        if not self.StopCrossOverUpdate:
            self.CrossOverReached = left_val > right_val

            if self.CrossOverReached:
                self.StopCrossOverUpdate = True
        else:
            if left_val < right_val:
                self.StopCrossOverUpdate = False

            self.CrossOverReached = False

        return self.CrossOverReached


class CrossBelow(object):
    def __init__(self):
        self.StopCrossOverUpdate = True
        self.CrossOverReached = False

    def evaluate(self, left_val: float, right_val: float) -> bool:
        if not self.StopCrossOverUpdate:
            self.CrossOverReached = left_val < right_val

            if self.CrossOverReached:
                self.StopCrossOverUpdate = True
        else:
            if left_val > right_val:
                self.StopCrossOverUpdate = False

            self.CrossOverReached = False

        return self.CrossOverReached
