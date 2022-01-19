from singleton_module import (
    simple_singleton,
    Singleton,
    SingletonMeta,
    NamedSingletonMeta,
    singleton,
    namedsingleton)



@simple_singleton
class TestSimpleFunCls: pass


class TestSimpleCls(Singleton): pass


class TestMetaCls(metaclass=SingletonMeta):

    def __init__(self):
        self.index = "test_index"

    @property
    def index_parm(self):
        return self.index

    @index_parm.setter
    def index_parm(self, i):
        self.index = i

# class TestMetaCls: pass


class TestMetaDiffCls(metaclass=SingletonMeta):

    def __init__(self):
        self.index = "test_index"

    @property
    def index_parm(self):
        return self.index

    @index_parm.setter
    def index_parm(self, i):
        self.index = i

# class TestMetaCls: pass


class TestNamedMetaCls(metaclass=NamedSingletonMeta):

    def __init__(self):
        self.index = "test_index"

    @property
    def index_parm(self):
        return self.index

    @index_parm.setter
    def index_parm(self, i):
        self.index = i

# class TestMetaCls: pass


class TestNamedMetaDiffCls(metaclass=NamedSingletonMeta):

    def __init__(self):
        self.index = "test_index"

    @property
    def index_parm(self):
        return self.index

    @index_parm.setter
    def index_parm(self, i):
        self.index = i

# class TestMetaCls: pass


@singleton
class TestCls: pass


@namedsingleton(name="test")
# @namedsingleton(name=1)
class TestNamedCls: pass


@namedsingleton(name="different")
# @namedsingleton(name=1)
class TestDiffNamedCls: pass


class NoSingletonTestCls: pass

