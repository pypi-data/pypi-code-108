from meili_sdk.websockets.client import MeiliWebsocketClient
from meili_sdk.websockets import constants
from meili_sdk.websockets.models.message import Message


def open_handler():
    print("Websocket is opened")


def on_close():
    print("WS CLOSED")


def on_error(*_):
    print("error has occurred")


client = MeiliWebsocketClient(
    "ca7a300d8180e1e771be54458fab8c01639a4cf8",
    override_host="wss://development.meilirobots.com",
    fleet=True,
    open_handler=open_handler,
    close_handler=on_close,
    error_handler=on_error,
)

client.add_vehicle("058a60e4f99d4bc3832d2b129270f745")
client.run_in_thread()

message = Message(
    event=constants.EVENT_LOCATION,
    value={"xm": 1, "ym": 1},
    vehicle="058a60e4f99d4bc3832d2b129270f745",
)

message.validate()

client.send(message)
