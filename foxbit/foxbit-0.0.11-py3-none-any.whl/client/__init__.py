import websocket
import datetime
from typing import Optional, Callable
from foxbit.frame import MessageFrame


class Client(websocket.WebSocketApp):
    """Client is a simple subclass of websocket.WebSocketApp class
    (from websocket-client module), where url parameter is
    wss://api.foxbit.com.br.

    Parameters
    ----------
    on_open: Callable
        Callback object which is called at opening websocket.
        on_open has one argument.
        The 1st argument is this class object. Example
        ```python
        def on_open(ws):
            print("connected")
        ```

    on_message: Callable
        Callback object which is called when received data.
        on_message has 2 arguments.
        The 1st argument is this class object.
        The 2nd argument is utf-8 data received from the server. Example
        ```python
        def on_message(ws, msg):
            frame = MessageFrame.fromJSON(msg)
            print(frame)
        ```
    on_error: Callable
        Callback object which is called when we get error.
        on_error has 2 arguments.
        The 1st argument is this class object.
        The 2nd argument is exception object. Example
        ```python
        def on_error(ws, err):
            print(err)
        ```
    on_close: Callable
        Callback object which is called when connection is closed.
        on_close has 3 arguments.
        The 1st argument is this class object.
        The 2nd argument is close_status_code.
        The 3rd argument is close_msg. Example:
        ```python
        def on_close(ws, status, msg):
            print("closed with status {}: {}".format(status, msg))
        ```

    enableTrace: bool
        Boolean object which enable websocket trace.
        Good for debbuging.
    """

    def __init__(
        self,
        on_open: Optional[Callable] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        enableTrace: Optional[bool] = False
    ) -> None:
        websocket.enableTrace(enableTrace)
        websocket.WebSocketApp.__init__(
            self,
            'wss://api.foxbit.com.br/',
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )


class PublicClient(Client):
    """PublicClient is a simple subclass of client.Client class
    (from foxbit.client module)

    All documentation is available at
    https://foxbit.com.br/wp-content/uploads/2018/07/Documentacao-api-fox-bit.pdf
    """

    def __init__(
        self,
        on_open: Optional[Callable] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        enableTrace: Optional[bool] = False
    ) -> None:
        Client.__init__(
            self,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            enableTrace=enableTrace
        )

    def getInstrument(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Retrieves the details of a specific
        instrument from the Order Management System
        of the trading venue. An instrument is a pair
        of exchanged products (or fractions of them)
        such as US dollars and ounces of gold.

        Parameters
        ----------
        OMSId: int
            The ID of the Order Management System f
            rom where the instrument is traded.

        InstrumentId: int
             The ID of the instrument.
        """

        frame = MessageFrame(
            endpoint='GetInstrument',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId
            }
        )
        self.send(frame.toJSON())

    def getInstruments(
        self,
        OMSId: Optional[int] = 1
    ) -> None:
        """Retrieves an array of instrument objects
        describing all instruments available on a trading
        venue to the user. An instrument is a pair of
        exchanged products (or fractions of them) such as US
        dollars and ounces of gold.

        Parameters
        ----------
        OMSId: int
            The Order Management System Id
        """

        frame = MessageFrame(
            endpoint='GetInstruments',
            payload={
                'OMSId': OMSId
            }
        )
        self.send(frame.toJSON())

    def getProducts(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Returns an array of products available
        on the trading venue. A product is an asset that is
        tradable or paid out.

        Parameters
        ----------
        OMSId: int
            The ID of the Order Management System
            for which the array of available
            products and currencies will be returned.

        InstrumentId: int
        """

        frame = MessageFrame(
            endpoint='GetProducts',
            payload={
                'OMSId': OMSId
            }
        )
        self.send(frame.toJSON())

    def getL2Snapshot(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1,
        Depth: Optional[int] = 100
    ) -> None:
        """Provides a current Level 2 snapshot
        of a specific instrument trading on an Order
        Management System to a user-determined market depth.

        The Level 2 snapshot allows the user to specify
        the level of market depth information on either side
        of the bid and ask.

        Parameters
        ----------
        OMSId: int
            The ID of the Order Management System
            where the instrument is traded

        InstrumentId: int
            The ID of the instrument that is
            the subject of the snapshot.

        Depth: int
            Depth in this call is “depth of market”,
            the number of buyers and sellers at greater
            or lesser prices in the order book for the instrument.
        """

        frame = MessageFrame(
            endpoint='GetL2Snapshot',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId,
                'Depth': Depth
            }
        )
        self.send(frame.toJSON())

    def getTickerHistory(
        self,
        InstrumentId: Optional[int] = 1,
        Interval: Optional[int] = 60,
        FromDate: Optional[datetime.datetime] = None,
        ToDate: Optional[datetime.datetime] = datetime.datetime.now()
    ) -> None:
        """Requests a ticker history
        (high, low, open, close, volume, bid, ask, ID)
        of a specific instrument from a given date forward to the present.
        You will need to format the returned data per your requirements.

        Parameters
        ----------

        InstrumentId: int
            The ID of a specific instrument.
            The Order Management System and the default Account
            ID of the logged-in user are assumed

        Interval: int
            Interval in seconds.
            Possible values are 60, 300, 900,
            1800, 3600, 21600, 43200, 86400, 604800

        FromDate: datetime.datetime
            Oldest date from which the ticker history will start.
            The method convert it to POSIX format and UTC time zone.
            The report moves toward the present from this point.

        ToDate: datetime.datetime
            Newest date from which the ticker history will go.
            The method convert it to POSIX format and UTC time zone.
            The report moves toward the present from this point.
        """

        _from = MessageFrame.buildValidPosixTimeString(FromDate)
        _to = MessageFrame.buildValidPosixTimeString(ToDate)

        frame = MessageFrame(
            endpoint='GetTickerHistory',
            payload={
                'InstrumentId': InstrumentId,
                'Interval': Interval,
                'FromDate': _from,
                'ToDate': _to
            }
        )
        self.send(frame.toJSON())
