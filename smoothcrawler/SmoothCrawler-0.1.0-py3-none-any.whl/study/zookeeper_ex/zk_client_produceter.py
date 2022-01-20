from kazoo.client import KazooClient, KazooState, KeeperState
import random
import time


Zookeeper_IP = "127.0.0.1:2181"

_zk_client = KazooClient(hosts=Zookeeper_IP)
_zk_client.start()

_node_path = "/my/test_zk/lucky_node"

_zk_client.ensure_path(path=_node_path)
if _zk_client.exists(path=_node_path) is False:
    _zk_client.create(path="/my/test_zk/node", value=b"Lucky Number Initial!")

while True:
    _random_index = f"lucky_{random.randrange(0, 100)}"
    print(f"[DEBUG] The lucky number we got at this time is {_random_index}.")
    _zk_client.set(path=_node_path, value=_random_index.encode("utf-8"))
    _sleep_time = random.randrange(5, 20)
    print(f"[DEBUG] It will sleep for {_sleep_time} seconds.")
    time.sleep(_sleep_time)

