import datetime
import threading

import jsonpickle

import websocket

from .algorum_types import *
from .concurrent_collections import *
from .remote_indicator_evaluator import *


class QuantEngineClient:
    MultiplyFactor = ((60 * 24) / 405)

    def __init__(self, url, apikey, launchmode, sid, user_id, trace_ws=False):
        self.Url = url
        self.ApiKey = apikey
        self.UserId = user_id
        self.LaunchMode = launchmode
        self.StrategyId = sid
        self.MessageHandlerMap = {}
        self.CorIdMessageMap = {}
        self.ws = None
        self.CorIdCounter = FastReadCounter()
        self.TickQueue = BoundedBlockingQueue(1000000)
        self.HandlerMessageQueue = BoundedBlockingQueue(1000000)
        self.stop_event = threading.Event()
        self.open_event = threading.Event()
        self.BacktestStartDate: datetime = datetime.utcnow()
        self.BacktestEndDate: datetime = datetime.utcnow()
        self.Evaluator = None
        self.LastProcessedTick = None
        self.ProgressPercent: float = 0.0
        self.Thread1 = None
        self.Thread2 = None
        self.Thread3 = None
        self.TraceWs = trace_ws

        self.add_message_handler("tick", self.tick_handler)
        self.add_message_handler("order_update", self.order_update_handler)
        self.add_message_handler("stop", self.stop_handler)
        self.add_message_handler("error", self.error_handler)

        self.Evaluator: RemoteIndicatorEvaluator

        self.initialize()

    @staticmethod
    def get_date_format(timestamp: str):
        if timestamp.find("Z") > 0:
            return "%Y-%m-%dT%H:%M:%SZ"
        else:
            return "%Y-%m-%dT%H:%M:%S"

    def execute_async(self,
                      algorum_websocket_message: AlgorumWebsocketMessage) -> \
            AlgorumWebsocketMessage:
        async_waiter = AsyncWaiter()
        self.CorIdMessageMap[algorum_websocket_message.CorId] = async_waiter
        self.ws.send(jsonpickle.encode(algorum_websocket_message, False))
        async_waiter.WaiterEvent.wait()

        if async_waiter.Message.MessageType == AlgorumMessageType.ErrorResponse:
            raise AlgorumException(async_waiter.Message)

        return async_waiter.Message

    def send_async(self, algorum_websocket_message: AlgorumWebsocketMessage):
        self.ws.send(jsonpickle.encode(algorum_websocket_message, False))

    def publish_stats(self, stats):
        self.send_async(AlgorumWebsocketMessage(
            "publish_stats",
            AlgorumMessageType.Oneway,
            self.CorIdCounter.increment(),
            jsonpickle.encode(stats, False),
            None
        ))

    def set_data(self, key: str, value):
        quant_data = QuantData(key, jsonpickle.encode(value, False))
        response = self.execute_async(AlgorumWebsocketMessage(
            "set_data",
            AlgorumMessageType.Request,
            self.CorIdCounter.increment(),
            jsonpickle.encode(quant_data, False),
            None
        ))

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

    def get_data(self, key: str):
        request = AlgorumWebsocketMessage('get_data',
                                          AlgorumMessageType.Request,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode(key, False), None)
        response = self.execute_async(request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        value = jsonpickle.decode(response.JsonData)
        return value

    def add_message_handler(self, name, handler):
        self.MessageHandlerMap[name] = handler

    def error_handler(self, algorum_websocket_message):
        msg = jsonpickle.decode(algorum_websocket_message.JsonData)
        self.on_error(msg)

    def tick_handler(self, algorum_websocket_message):
        tick_data = jsonpickle.decode(algorum_websocket_message.JsonData)
        tick_data_obj = TickData(**tick_data)
        tick_data_obj.AlgorumMessage = algorum_websocket_message
        self.TickQueue.enqueue(tick_data_obj)

    def order_update_handler(self, algorum_websocket_message):
        order_dict = jsonpickle.decode(algorum_websocket_message.JsonData)
        order = Order(**order_dict)
        self.on_order_update(order)

        algorum_websocket_message.MessageType = AlgorumMessageType.Response
        algorum_websocket_message.JsonData = ""
        self.ws.send(jsonpickle.encode(algorum_websocket_message))

    def stop_handler(self, algorum_websocket_message):
        algorum_websocket_message.MessageType = AlgorumMessageType.Response
        algorum_websocket_message.JsonData = ""
        self.ws.send(jsonpickle.encode(algorum_websocket_message))
        self.stop_event.set()

    def wait(self):
        self.stop_event.wait()

    def subscribe_symbols(self, symbols):
        sub_symbols_request = \
            AlgorumWebsocketMessage('sub_symbols',
                                    AlgorumMessageType.Request,
                                    self.CorIdCounter.increment(),
                                    jsonpickle.encode(symbols, False), None)
        # print(sub_symbols_request)
        response = self.execute_async(sub_symbols_request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])
        # print(response)

    def log(self, log_level: str, message: str):
        request = AlgorumWebsocketMessage('log',
                                          AlgorumMessageType.Oneway,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode({
                                              'LogLevel': log_level,
                                              'Message': message
                                          }, False), None)
        self.send_async(request)

    def backtest(self, backtest_request: BacktestRequest):
        self.BacktestStartDate = backtest_request.StartDate
        self.BacktestEndDate = backtest_request.EndDate

        msg_request = \
            AlgorumWebsocketMessage('backtest',
                                    AlgorumMessageType.Request,
                                    self.CorIdCounter.increment(),
                                    jsonpickle.encode(backtest_request, False), None)
        # print(msg_request)
        response = self.execute_async(msg_request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        # print(response)

    def start_trading(self, trading_request: TradingRequest):
        msg_request = \
            AlgorumWebsocketMessage('start_trading',
                                    AlgorumMessageType.Request,
                                    self.CorIdCounter.increment(),
                                    jsonpickle.encode(trading_request, False), None)
        # print(msg_request)
        response = self.execute_async(msg_request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

    def get_holidays(self, exchange: TradeExchange):
        request = AlgorumWebsocketMessage('get_holidays',
                                          AlgorumMessageType.Request,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode(exchange, False), None)
        # print(request)
        response = self.execute_async(request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        # print(response)
        holiday_list = jsonpickle.decode(response.JsonData)
        # print(holiday_list)
        return holiday_list

    def get_options_chain(self, ticker):
        request = AlgorumWebsocketMessage('get_options_chain',
                                          AlgorumMessageType.Request,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode(ticker, False), None)
        # print(request)
        response = self.execute_async(request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        options_chain = jsonpickle.decode(response.JsonData)
        return options_chain

    def place_order(self, place_order_request: PlaceOrderRequest):
        request = AlgorumWebsocketMessage('place_order',
                                          AlgorumMessageType.Request,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode(place_order_request, False), None)
        # print(request)
        response = self.execute_async(request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        # print(response)
        order_id = jsonpickle.decode(response.JsonData)
        # print(order_id)
        return order_id

    def cancel_order(self, order_id: str) -> bool:
        request = AlgorumWebsocketMessage('cancel_order',
                                          AlgorumMessageType.Request,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode(order_id, False), None)
        # print(request)
        response = self.execute_async(request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        result: bool = jsonpickle.decode(response.JsonData)
        return result

    def create_indicator_evaluator(self, create_indicator_request: CreateIndicatorRequest) \
            -> RemoteIndicatorEvaluator:
        request = AlgorumWebsocketMessage('create_indicator_evaluator',
                                          AlgorumMessageType.Request,
                                          self.CorIdCounter.increment(),
                                          jsonpickle.encode(create_indicator_request, False), None)
        # print(request)
        response = self.execute_async(request)

        if response.MessageType == AlgorumMessageType.ErrorResponse:
            raise Exception(response.Error['ErrorMessage'])

        # print(response)

        uid = jsonpickle.decode(response.JsonData)
        # print(uid)

        self.Evaluator = RemoteIndicatorEvaluator(
            self,
            create_indicator_request.Symbol, uid)
        return self.Evaluator

    def get_stats(self, tick_data: TickData):
        raise NotImplementedError(self)

    def send_progress_async(self, tick_data: TickData):
        t_seconds = (self.BacktestEndDate - self.BacktestStartDate).total_seconds() * (70 / 100)
        processed_seconds = (datetime.strptime(tick_data.Timestamp,
                                               QuantEngineClient.get_date_format(tick_data.Timestamp)) -
                             datetime.strptime(self.LastProcessedTick.Timestamp,
                                               QuantEngineClient.get_date_format(self.LastProcessedTick.Timestamp))).total_seconds() * QuantEngineClient.MultiplyFactor

        progress_percent = (processed_seconds / t_seconds) * 100

        if (self.ProgressPercent + progress_percent >= 100) and not tick_data.LastTick:
            progress_percent = 0
        else:
            if tick_data.LastTick:
                self.ProgressPercent = 100

        if progress_percent >= 0.1 or progress_percent == 0 or tick_data.LastTick:
            if not tick_data.LastTick:
                self.ProgressPercent += progress_percent

            self.send_async(AlgorumWebsocketMessage(
                'publish_progress',
                AlgorumMessageType.Oneway,
                self.CorIdCounter.increment(),
                jsonpickle.encode(self.ProgressPercent, False), None))

            stats = self.get_stats(tick_data)
            self.publish_stats(stats)

            print('>>>>>>>>> Progress: ' + str(self.ProgressPercent))

            for k, v in stats.items():
                print('Key: ' + str(k) + ', Value: ' + str(v))

            self.LastProcessedTick = tick_data

        if self.ProgressPercent >= 100:
            self.log(LogLevel.Information, "100% Progress")
            self.stop_event.set()
            self.ws.close()

    def run(self):
        self.ws.run_forever()

    def on_error(self, msg: str):
        print(msg)

    def on_tick(self, tick_data: TickData):
        raise NotImplementedError(self)

    def on_order_update(self, order: Order):
        raise NotImplementedError(self)

    def process_tick(self):

        while 1:
            tick_data = self.TickQueue.dequeue()
            algorum_websocket_message = tick_data.AlgorumMessage
            tick_data.AlgorumMessage = None

            if tick_data is not None:
                last_processed_tick: TickData = self.LastProcessedTick

                if (self.LastProcessedTick is None) or \
                        (datetime.strptime(last_processed_tick.Timestamp,
                                           QuantEngineClient.get_date_format(last_processed_tick.Timestamp)).day !=
                         datetime.strptime(tick_data.Timestamp, QuantEngineClient.get_date_format(tick_data.Timestamp)).day):
                    self.LastProcessedTick = tick_data

                self.on_tick(tick_data)

                algorum_websocket_message.MessageType = AlgorumMessageType.Response
                algorum_websocket_message.JsonData = ""
                self.ws.send(jsonpickle.encode(algorum_websocket_message))
            else:
                break

    def handle_message(self):

        while 1:
            algorum_websocket_message = self.HandlerMessageQueue.dequeue()

            if algorum_websocket_message.Name in self.MessageHandlerMap:
                handler = self.MessageHandlerMap[algorum_websocket_message.Name]
            else:
                handler = None

            if handler is not None:
                handler(algorum_websocket_message)

    def initialize(self):
        def on_message(ws, message):
            # diagnostic message
            # print(message)

            msg_dict = jsonpickle.decode(message)
            msg = AlgorumWebsocketMessage(**msg_dict)

            if msg.Name in self.MessageHandlerMap:
                handler = self.MessageHandlerMap[msg.Name]
            else:
                handler = None

            if handler is None:
                if msg.MessageType == AlgorumMessageType.Request:
                    msg.MessageType = AlgorumMessageType.Response
                    msg.JsonData = ""
                    self.ws.send(jsonpickle.encode(msg))
                else:
                    if msg.MessageType == AlgorumMessageType.Response or \
                            msg.MessageType == AlgorumMessageType.ErrorResponse:
                        if msg.CorId in self.CorIdMessageMap:
                            async_waiter = self.CorIdMessageMap[msg.CorId]
                            async_waiter.Message = msg
                            del self.CorIdMessageMap[msg.CorId]
                            async_waiter.WaiterEvent.set()
            else:
                self.HandlerMessageQueue.enqueue(msg)

        def on_error(ws, error):
            print(error)

        def on_close(ws, error, msg):
            print('websockets closed')
            print(error)
            print(msg)
            self.stop_event.set()

        def on_open(ws):
            print('open')
            self.open_event.set()

        if self.TraceWs is None:
            self.TraceWs = False

        websocket.enableTrace(self.TraceWs)

        self.ws = websocket.WebSocketApp(self.Url,
                                         on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close,
                                         header={"x-algorum-userid": self.UserId})
        self.ws.on_open = on_open

        self.Thread1 = threading.Thread(target=self.run, daemon=True)
        self.Thread1.start()
        self.Thread2 = threading.Thread(target=self.process_tick, daemon=True)
        self.Thread2.start()
        self.Thread3 = threading.Thread(target=self.handle_message, daemon=True)
        self.Thread3.start()

        self.open_event.wait()
