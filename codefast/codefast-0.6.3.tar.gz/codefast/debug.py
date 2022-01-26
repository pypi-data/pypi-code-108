from typing import List, Callable, Dict


class Debug(object):
    """ A class for faster, more robust debugging.
    """

    def __init__(self):
        self.funcs = {}
        self.results = {}
        self.whitelist = []

    def register(self, f: Callable, *args, **kwargs):
        """ Register a function to be called when the program exits.
        """
        self.funcs[f] = (args, kwargs)

    def run(self):
        for f in self.whitelist:
            if f in self.funcs:
                resp = f(*self.funcs[f][0], **self.funcs[f][1])
                self.results[f.__name__] = resp
            else:
                raise Exception(f'Function {f} not registered.')


if __name__ == '__main__':
    pass
