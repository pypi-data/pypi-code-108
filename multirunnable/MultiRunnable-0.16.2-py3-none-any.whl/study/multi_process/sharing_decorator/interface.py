from multirunnable._singletons import (
    simple_singleton,
    singleton, Singleton, ConnectionPoolSingleton,
    SingletonMeta, NamedSingletonMeta, NamedSingletonABCMeta)



class MarkerCls(metaclass=NamedSingletonABCMeta):
    pass

