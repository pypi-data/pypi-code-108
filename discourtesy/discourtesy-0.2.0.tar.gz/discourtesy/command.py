class Command:
    def __init__(self, name, coroutine, followup, input_type):
        self.name = name
        self.coroutine = coroutine

        self.followup = followup
        self.input_type = input_type


def command(name, followup=False, input_type=1):
    def decorator(coroutine):
        return Command(name, coroutine, followup, input_type)

    return decorator
