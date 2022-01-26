# exceptions.py 

# Define the exception for cancelling an uncancellable event.
class UncancellableEvent(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
