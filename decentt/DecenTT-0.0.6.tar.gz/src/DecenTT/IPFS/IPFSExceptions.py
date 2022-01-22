import platform


class TopicIncompatibleType(Exception):
    """
        Subjected Topic is not a compatible type
    """
    def __str__(self):
        return f"Topic should either be a string or a list!"


class UnsupportedPlatform(Exception):
    """
        Subjected Platform is currently not supported by the IPFS installer.
    """

    def __str__(self):
        return f"{platform.system()} is currently not supported by the IPFS installer."


class InvalidCallback(Exception):
    """
        Subjected Callback is not a valid callback
    """

    def __init__(self, callback) -> None:
        self.called_callback = callback

    def __str__(self):
        return f"{self.called_callback.__name__} is not a valid Function!"
