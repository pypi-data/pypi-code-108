class EngineBase:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def connection(self, *args, **kwargs):
        raise NotImplementedError()

    def execute(self, query, params):
        raise NotImplementedError()

    def fetchone(self, query, params):
        raise NotImplementedError()

    def fetchall(self, query, params):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def begin(self):
        raise NotImplementedError()

    def rollback(self):
        raise NotImplementedError()

    def mogrify(self, query, params):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()