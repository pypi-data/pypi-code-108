
class _Debug:
    def __call__(self, attrviewer=False, itercount=None, iterdepth=None):
        from .debug import Debug
        debug = Debug(attrviewer, itercount, iterdepth)
        return debug

class _Torchbug:
    def __call__(self):
        from .torchbug import Torchbug
        torchbug = Torchbug()
        return torchbug

Debug = _Debug()
Torchbug = _Torchbug()
