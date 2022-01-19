import logging


class ExampleFilter(logging.Filter):
    """ExampleFilter."""

    def filter(self, record):
        # You can filter out the record based on your requirements.
        return True
