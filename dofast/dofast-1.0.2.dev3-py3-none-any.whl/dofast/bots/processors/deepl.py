import codefast as cf
from dofast.bots.processors.base import TextProcessor
from dofast.utils import DeeplAPI
from telegram import Update


class DeeplProcessor(TextProcessor):
    """Translate with Deepl
    """
    def __init__(self) -> None:
        self.deeplapi = DeeplAPI()

    def match(self, _text: str) -> bool:
        if _text.startswith('http'):
            return False
        return True

    def run(self, text: str, update: Update) -> str:
        update.message.reply_text(
            self.deeplapi.translate(text)['translations'].pop()['text'])
        return True
