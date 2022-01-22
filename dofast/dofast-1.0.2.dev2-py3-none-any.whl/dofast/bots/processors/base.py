from abc import ABCMeta, abstractmethod
from typing import List

import codefast as cf
from celery.states import FAILURE
from telegram import Update


class TextProcessor(metaclass=ABCMeta):
    '''Base class for processing text passed from user'''
    def match(self, text: str) -> bool:
        pass

    def process(self, text: str, update: Update) -> str:
        if self.match(text):
            return self.run(text, update)

    @abstractmethod
    def run(self, text: str, update: Update) -> bool:
        return False
