class nameNotFoundError(Exception):
    def __init__(self, name):
        self.name = name
        self.__str__()

    def __str__(self):
        return 'The {} parameter must exist.'.format(self.name)
