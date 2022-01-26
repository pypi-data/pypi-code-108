

def _fix_logging(handler):
    handler._builtin_open = open

    def _new_open(self):
        open_func = self._builtin_open
        return open_func(self.baseFilename, self.mode)

    setattr(handler, "_open", _new_open)
