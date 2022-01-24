class UnexpectedCapabilities(Exception):
    pass


class ActorListenBreaker(Exception):
    pass


class ActorPoisoned(ActorListenBreaker):
    pass


class NotEnoughResources(Exception):
    pass


class NotEnoughResourcesToContinue(NotEnoughResources):
    pass
