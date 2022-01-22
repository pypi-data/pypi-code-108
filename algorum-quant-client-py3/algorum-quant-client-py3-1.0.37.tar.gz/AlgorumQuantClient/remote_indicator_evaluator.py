from datetime import datetime

import jsonpickle

from .algorum_types import *


class RemoteIndicatorEvaluator(object):
    def __init__(self, client,
                 symbol: TradeSymbol,
                 uid: str):
        self.Uid = uid
        self.Symbol = symbol
        self.Client = client

    def clear_candles(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'clear_indicator_candles',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(self.Uid, False), None))
        return

    def rsi(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'RSI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def ema(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'EMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def abandoned_baby_bear(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ABANDONEDBABYBEAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def abandoned_baby_bull(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ABANDONEDBABYBULL',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def ad(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'AD',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def adosc(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ADOSC',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def adx(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ADX',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def adxr(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ADXR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def ao(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'AO',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def apo(self, short_period: float, long_period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'APO',
                            {
                                'shortPeriod': short_period,
                                'longPeriod': long_period
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def aroon_down(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'AROONDOWN',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def aroon_osc(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'AROONOSC',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def aroon_up(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'AROONUP',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def atr(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ATR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def avg_price(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'AVGPRICE',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def bband_lower(self, period: float, stddev: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'BBANDLOWER',
                            {
                                'period': period,
                                'stddev': stddev
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def bband_mid(self, period: float, stddev: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'BBANDMID',
                            {
                                'period': period,
                                'stddev': stddev
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def bband_up(self, period: float, stddev: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'BBANDUP',
                            {
                                'period': period,
                                'stddev': stddev
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def big_black_candle(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'BIGBLACKCANDLE',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def black_marubozu(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'BLACKMARUBOZU',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def bop(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'BOP',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def candle_close(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'CANDLECLOSE',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def candle_high(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'CANDLEHIGH',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def candle_low(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'CANDLELOW',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def candle_open(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'CANDLEOPEN',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def cci(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'CCI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def close(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('CLOSE', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def cos(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'COS',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def dema(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'DEMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def doji(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'DOJI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def dragonfly_doji(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'DRAGONFLYDOJI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def ema(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'EMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def engulfing_bear(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ENGULFINGBEAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def engulfing_bull(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ENGULFINGBULL',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def evening_doji_star(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'EVENINGDOJISTART',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def evening_star(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'EVENINGSTAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def four_price_doji(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'FOURPRICEDOJI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def grave_stone_doji(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'GRAVESTONEDOJI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def hammer(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'HAMMER',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def hanging_man(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'HANGINGMAN',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def high(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('HIGH', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def hma(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'HMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def inverted_hammer(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'INVERTEDHAMMER',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def kama(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'KAMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def long_legged_doji(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'LONGLEGGEDDOJI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def low(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('LOW', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def macd(self, short_period: float, long_period: float, signal_period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MACD',
                            {
                                'shortPeriod': short_period,
                                'longPeriod': long_period,
                                'signalPeriod': signal_period
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def macd_signal(self, short_period: float, long_period: float, signal_period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MACDSIGNAL',
                            {
                                'shortPeriod': short_period,
                                'longPeriod': long_period,
                                'signalPeriod': signal_period
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def marubozu(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MARUBOZU',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def md(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MD',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def mfi(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MFI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def minus_dmi(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MINUSDMI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def mom(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MOM',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def morning_doji_star(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MORNINGDOJISTAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def morning_star(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'MORNINGSTAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def natr(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'NATR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def obv(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'OBV',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def open(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('OPEN', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def plus_dmi(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'PLUSDMI',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def ppo(self, short_period: float, long_period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'PPO',
                            {
                                'shortPeriod': short_period,
                                'longPeriod': long_period
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def prev_close(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('PREVCLOSE', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def prev_high(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('PREVHIGH', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def prev_low(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('PREVLOW', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def prev_open(self):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest('PREVOPEN', None)
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def psar(self, period: float, accl_factor_step: float, accl_factor_max: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'PSAR',
                            {
                                'period': period,
                                'acclFactorStep': accl_factor_step,
                                'acclFactorMax': accl_factor_max
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def roc(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ROC',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def sin(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'SIN',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def sma(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'SMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def spinning_top(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'SPINNINGTOP',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def star(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'STAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def stddev(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'STDDEV',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def stoch_d(self, period: float, slowing_period: float, period_2: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'STOCHD',
                            {
                                'period': period,
                                'slowingPeriod': slowing_period,
                                'period2': period_2
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def stoch_k(self, period: float, slowing_period: float, period_2: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'STOCHK',
                            {
                                'period': period,
                                'slowingPeriod': slowing_period,
                                'period2': period_2
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def sub(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'SUB',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def sum(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'SUM',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def support_resistance(self, period: float, level: float, backtrack_candles: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'SUPPORTRESISTANCE',
                            {
                                'period': period,
                                'level': level,
                                'backtrackCandles': backtrack_candles
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["ResultMap"]["support"], \
               result_val[0]["ResultMap"]["supportscore"], \
               result_val[0]["ResultMap"]["resistance"], \
               result_val[0]["ResultMap"]["resistancescore"]

    def tan(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TAN',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def tema(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TEMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def three_black_crows(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'THREEBLACKCROWS',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def three_white_soldiers(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'THREEWHITESOLDIERS',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def tra(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TRA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def trend(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TREND',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"], result_val[0]["ResultMap"]["strength"]

    def trima(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TRIMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def trix(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TRIX',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def tsf(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'TSF',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def uosc(self, short_period: float, medium_period: float, long_period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'UOSC',
                            {
                                'shortPeriod': short_period,
                                'mediumPeriod': medium_period,
                                'longPeriod': long_period
                            }
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def var(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'VAR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def volatility(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'VOLATILITY',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def vwma(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'VWMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def white_marubozu(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'WHITEMARUBOZU',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def will_r(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'WILLR',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def wma(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'WMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def zlema(self, period: float):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'get_indicators',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                GetIndicatorsRequest(
                    self.Uid,
                    [
                        IndicatorRequest(
                            'ZLEMA',
                            {'period': period}
                        )
                    ]
                ), False), None))
        result_val = jsonpickle.decode(response.JsonData)
        return result_val[0]["Result"]

    def preload_candles(self, candle_count: int, preload_end_time: datetime, api_key: str,
                        api_secret_key: str):
        response = self.Client.execute_async(AlgorumWebsocketMessage(
            'preload_candles',
            AlgorumMessageType.Request,
            self.Client.CorIdCounter.increment(),
            jsonpickle.encode(
                PreloadCandlesRequest(self.Uid, candle_count, preload_end_time, api_key, api_secret_key),
                False), None))
