from sdsRayanArvin.Request import Request


class Api:

    def __init__(self, requestClass: Request):
        self.Request = requestClass

    def instanceOfRepository(self, repositoryClass):
        """
        :return: :class:`repositoryClass <repositoryClass>` object
        """
        return repositoryClass(self.Request)
