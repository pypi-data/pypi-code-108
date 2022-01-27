from koil import koil


class GrantException(Exception):
    pass


class FaktsGrant:


    async def aload(self, previous = {}, **kwargs):
        raise NotImplementedError()

    def load(self, previous ={}, as_task=False, **kwargs):
        return koil(self.load(previous=previous, **kwargs), as_task=as_task)
