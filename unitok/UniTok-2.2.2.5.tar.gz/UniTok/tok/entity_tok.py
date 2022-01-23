from .tok import BaseTok
from UniTok.vocab.vocab import Vocab


class EntTok(BaseTok):
    def t(self, obj):
        if self.pre_handler:
            obj = self.pre_handler(obj)
        return self.vocab.append(str(obj))
