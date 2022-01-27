from koil import koil


class MiddlewareException(Exception):
    pass


class FaktsMiddleware:


    async def aparse(self, previous = {}, **kwargs):
        raise NotImplementedError()

    def parse(self, previous ={}, as_task=False, **kwargs):
        return koil(self.aparse(previous=previous, **kwargs), as_task=as_task)
