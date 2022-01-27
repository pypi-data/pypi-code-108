from rox.core.analytics import Client


class ClientProxy:
    def __init__(self, device_properties, write_key):
        self.device_properties = device_properties
        self.write_key = write_key
        self.client = None

    def track(self, event):
        if self.client is None:
            self.client = Client(self.device_properties, self.write_key)

        self.client.track(event)

    def shutdown(self):
        if self.client is not None:
            self.client.shutdown()
