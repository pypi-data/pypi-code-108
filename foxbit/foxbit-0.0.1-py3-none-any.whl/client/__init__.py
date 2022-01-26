import websocket
from typing import Optional, Callable


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
