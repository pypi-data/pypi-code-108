class MQTTValueError(Exception):
    """Wrong Value argument error"""
    pass


class InvalidCallback(Exception):
    """
        Subjected Callback is not a valid callback
    """

    def __init__(self, callback) -> None:
        self.called_callback = callback

    def __str__(self):
        return f"{self.called_callback.__name__} is not a valid Function!"
