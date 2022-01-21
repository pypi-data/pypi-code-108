# 2020-02-18. Leonardo Molina.
# 2021-10-12. Last modified.

from .flexible import Flexible

class Subscription:
    def __init__(self, publisher):
        self.publisher = publisher
    
    def unsubscribe(self):
        self.publisher.unsubscribe(self);

class Publisher:
    def __init__(self):
        p = self.__private = Flexible()
        
        p.subscriptionToEvent = {}
        p.eventToSubscriptions = {}
        p.subscriptionToCallback = {}
        pass
    
    def contains(self, event):
        p = self.__private
        return event in p.eventToSubscriptions
    
    # subscription = subscribe(event, callback)
    def subscribe(self, event, callback):
        p = self.__private
        subscription = Subscription(self)
        if event not in p.eventToSubscriptions:
            p.eventToSubscriptions[event] = []
        p.eventToSubscriptions[event].append(subscription)
        p.subscriptionToCallback[subscription] = callback
        p.subscriptionToEvent[subscription] = event
        return subscription
    
    # unsubscribe(subscription)
    def unsubscribe(self, subscription):
        p = self.__private
        if subscription in p.subscriptionToEvent:
            event = p.subscriptionToEvent[subscription]
            p.eventToSubscriptions[event].remove(subscription)
            del p.subscriptionToEvent[subscription]
            del p.subscriptionToCallback[subscription]
    
    # invoke(event)
    def invoke(self, event, *args, **kargs):
        p = self.__private
        if event in p.eventToSubscriptions:
            for subscription in p.eventToSubscriptions[event]:
                callback = p.subscriptionToCallback[subscription]
                callback(*args, **kargs)
                
if __name__ == "__main__":
    publisher = Publisher()
    subscription1 = publisher.subscribe("EventA", lambda : print('Called 1!'))
    subscription2 = publisher.subscribe("EventA", lambda : print('Called 2!'))
    subscription3 = publisher.subscribe("EventB", lambda message : print(message))
    subscription1.unsubscribe()
    publisher.invoke("EventA")
    publisher.invoke("EventB", "Hello!")