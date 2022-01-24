# The default protocol used
PROTOCOL = "nats"
# The default host used to connect
HOST = "127.0.0.1"
# The default ports used to connect
PORTS = {
    "nats": 4222,
    "mqtt": 1883,
    "redis": 6379,
    "memory": 0,
}
# The default delay between two pings
PING_INTERVAL = 120
# Number of oustanding pings for which no pong is received before reconnecting
MAX_OUTSTANDING_PINGS = 2
# Allow reconnect by default
ALLOW_RECONNECT = True
# Maximum number of reconnection attempts allowed
MAX_RECONNECT_ATTEMPS = 60
# Maximum timeout to wait before cancelling current connection attempt
CONNECT_TIMEOUT = 2
# Maximum timeout to wait before cancelling current reconnection attempt
RECONNECT_TIMEOUT = 2
# Maximum timeout to wait before closing subscriptions when draining
DRAIN_TIMEOUT = 30
# Maximum size of the flusher queue
FLUSHER_QUEUE_SIZE = 1024

CONCURRENT_REQUESTS_LIMIT = 1
PENDING_REQUESTS_LIMIT = 1
PENDING_BYTES_LIMIT = 1024
