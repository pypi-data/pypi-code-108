from kazoo.client import KazooClient, KazooState, KeeperState


Zookeeper_IP = "127.0.0.1:2181"

# Initial a Zookeeper client and activate it.
_zk_client = KazooClient(hosts=Zookeeper_IP)
_zk_client.start()

# Get the state of client.
_state = _zk_client.state
print(f"[DEBUG] _state: {_state}")

# Ensure the target path exists.
_zk_client.ensure_path(path="/my/test_zk")
# Create and assign a value into target path (node).
_zk_client.create(path="/my/test_zk/node", value=b"Yee~~~~")

# Get the value of the target path (node).
data, stat = _zk_client.get("/my/test_zk")
print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

# Get the children info of target path (node).
children = _zk_client.get_children("/my/test_zk")
print("There are %s children with names %s" % (len(children), children))


# Set a Zookeeper listener
@_zk_client.add_listener
def test_listener(state):
    if state == KazooState.CONNECTED:
        if state == KeeperState.CONNECTED_RO:
            print("Read only mode!")
        else:
            print("Read / Write mode!")


# Set a Zookeeper "Data" Watcher of target path (node).
@_zk_client.DataWatch("/my/test_zk")
def test_data_watcher(data, state):
    print("Version: %s, data: %s" % (state.version, data.decode("utf-8")))


# Set a Zookeeper "Children" Watcher of target path (node).
@_zk_client.ChildrenWatch("/my/test_zk/node")
def test_child_watcher(child):
    print("Children are now: %s" % child)

