import json


class MQCommand:
    COMMAND_ENQUEUE = 'ENQUEUE'
    COMMAND_DEQUEUE = 'DEQUEUE'

    def __init__(self, command: str, queue_name: str, value: str = None):
        self.command = command
        self.queue_name = queue_name
        self.value = value

    @staticmethod
    def parse(data: bytes):
        decoded = data.decode()
        x = json.loads(decoded)
        if type(x) is not dict:
            return None
        command = x.get('command')
        queue_name = x.get('queue_name')
        value = x.get('value')

        if command != MQCommand.COMMAND_DEQUEUE and command != MQCommand.COMMAND_ENQUEUE:
            return None

        if type(queue_name) is not str or len(queue_name) <= 0:
            return None

        if command == MQCommand.COMMAND_ENQUEUE and value is None:
            return None

        return MQCommand(command, queue_name, value)

    def package_as_bytes(self) -> bytes:
        x = json.dumps({'command': self.command, 'queue_name': self.queue_name, 'value': self.value})
        return x.encode()
