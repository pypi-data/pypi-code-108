class NehushtanWebsocketConnectionEntity:
    def __init__(self, websocket):
        self.__local_key = f'{websocket.local_address[0]}-{websocket.local_address[1]}'
        self.__remote_key = f'{websocket.remote_address[0]}-{websocket.remote_address[1]}'
        self.__websocket = websocket

    def get_local_key(self):
        return self.__local_key

    def get_remote_key(self):
        return self.__remote_key

    def get_key(self):
        return f'{self.__local_key}~{self.__remote_key}'

    def get_websocket(self):
        return self.__websocket
