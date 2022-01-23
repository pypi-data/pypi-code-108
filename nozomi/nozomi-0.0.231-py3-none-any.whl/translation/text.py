"""
Nozomi
Text Module
author: hugh@blinkybeach.com
"""
from nozomi.translation.language import Language


class Text:

    def __init__(
        self,
        body: str,
        language: Language
    ) -> None:

        self._body = body
        self._language = language

        return

    def is_in_language(
        self,
        language: Language,
        strict_variant: bool = False
    ) -> bool:
        if self._language == language:
            return True
        if strict_variant is False:
            if language.iso_639_1 == self._language.iso_639_1:
                return True
        return False
