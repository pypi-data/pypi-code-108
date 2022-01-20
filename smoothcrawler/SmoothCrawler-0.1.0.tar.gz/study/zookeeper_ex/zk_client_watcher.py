from kazoo.client import KazooClient, KazooState, KeeperState
import random
import time


Zookeeper_IP = "127.0.0.1:2181"

_zk_client = KazooClient(hosts=Zookeeper_IP)
_zk_client.start()

_node_path = "/my/test_zk/lucky_node"
_lucky_number = [f"lucky_{random.randrange(0, 100)}" for _ in range(10)]

while True:
    @_zk_client.DataWatch(_node_path)
    def test_data_watcher(data, state):
        print("Version: %s, data: %s" % (state.version, data.decode("utf-8")))
        if data.decode("utf-8") in _lucky_number:
            print(f"[DEBUG] You got the lucky number!")
        time.sleep(1)



# @_zk_client.ChildrenWatch("/my/test_zk/node")
# def test_child_watcher(child):
#     print("Children are now: %s" % child)

