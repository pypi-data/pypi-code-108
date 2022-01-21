LISTEN_ADDRESS = "0.0.0.0"
HOST = "localhost"
PORT = 8083
LOCATION = "/ws"
SECRET_KEY = "NOT_SET"

RABBIT_SERVER = {
    "USER": "guest",
    "PASSWORD": "guest",
    "SERVER": {
        "HOST": HOST,
        "PORT": 5672,
        "VHOST": "/"
    },
    "EXCHANGE_NAME": "sockjs",
    "EXCHANGE_TYPE": "direct",
    "QUEUE_NAME": "ws01"
}
REDIS_SERVER = {
    "HOST": HOST,
    "PORT": 6379,
    "DB": 0,
    "PASSWORD": None,
    "PREFIX": "sockjs:"
}
