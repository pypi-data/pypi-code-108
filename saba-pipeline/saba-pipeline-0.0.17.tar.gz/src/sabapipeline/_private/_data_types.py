class Server:
    def __init__(self,
                 address: str,
                 port: int
                 ):
        self.address = address
        self.port = port

    def __str__(self):
        return f'{self.address}:{self.port}'
