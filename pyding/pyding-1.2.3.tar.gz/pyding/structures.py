#structures.py
from .exceptions import UncancellableEvent
from .variables import events, async_events


# Wrapper for event handlers
class EventHandler:
    def __init__(self, function, event, priority, additional_kwargs={}):
        self.function = function
        self.event = event
        self.priority = priority
        self.additional_kwargs = additional_kwargs


    def register(self, additional_kwargs={}):
        if self.event not in events:
            events[self.event] = {}
        
        # Check if the priority is already registered.
        if self.priority not in events[self.event]:
            events[self.event][self.priority] = []

        events[self.event][self.priority].append(self)

        self.additional_kwargs = self.additional_kwargs | additional_kwargs

    def unregister(self):
        events[self.event][self.priority].remove(self)

    def call(self, call, args, kwargs):
        kwargs = kwargs | self.additional_kwargs
        return self.function(call, *args, **kwargs)

# Add support for event calls inside objects
class EventSupport:
    def __init__(self):
        self.register_events()

    def register_events(self):
        for method in self.__dir__():
            method = self.__getattribute__(method)
            if isinstance(method, EventHandler):
                method.register({"self": self})



# Define the EventCall class
class EventCall:
    def __init__(self, event_name, cancellable=False):
        self.__name = event_name
        self.__cancelled = False
        self.cancellable = cancellable        
        self.response = None
    
    # Cancelling is only one-way. 
    def cancel(self):
        if self.cancellable:
            self.__cancelled = True
            return
        raise UncancellableEvent(f'{self.event_name} is not an cancellable event.')
    
    # Using it as a property since we don't want it to be writable 
    @property
    def cancelled(self):
        return self.__cancelled

    @property
    def name(self):
        return self.__name
    
    def __repr__(self):
        return f'<EventCall _name={self.name!r} _cancelled={self.cancelled!r} _response={self.response!r}>'