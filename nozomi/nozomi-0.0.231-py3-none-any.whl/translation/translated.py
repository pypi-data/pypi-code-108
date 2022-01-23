"""
Nozomi
Translated Module
author: hugh@blinkybeach.com
"""
from nozomi.translation.language import Language
from typing import List, Optional
from nozomi.translation.text import Text


class Translated:
    """
    Abstract protocol definining an interfaces for translated text strings
    """
    translated_text: List[Text] = NotImplemented

    def in_language(self, language: Language) -> Optional[str]:
        # First try for a strict variant, then fall back to a language match
        for text in self.translated_text:
            if text.is_in_language(language, strict_variant=True):
                return text
            continue
        for text in self.translated_text:
            if text.is_in_language(language, strict_variant=False):
                return text
            continue
        return None
