"""
Nozomi
Language Module
author: hugh@blinkybeach.com
"""
from nozomi.http.headers import Headers
from typing import TypeVar, Type, Optional, List
from nozomi.http.accept_language import AcceptLanguage

T = TypeVar('T', bound='Language')


class Language:
    """
    Abstract class to be adopted by an application Language
    class
    """
    _ACCEPT_HEADER = 'Accept-Language'

    iso_639_1: str = NotImplemented
    variant_code: str = NotImplemented

    def __eq__(self, other) -> bool:
        if (
            self.iso_639_1 == other.iso_639_1
            and self.variant_code == other.variant_code
        ):
            return True
        return False

    @classmethod
    def with_iso_639_1_and_variant(
        cls: Type[T],
        languages: List[T],
        iso_639_1: str,
        variant_code: Optional[str],
        fallback: Optional[T]
    ) -> Optional[T]:

        if languages is None or len(languages) < 1:
            return fallback

        for language in languages:
            if language.iso_639_1.lower() == iso_639_1.lower():
                if language.variant_code.lower() == variant_code.lower():
                    return language
                continue
            continue

        return fallback

    @classmethod
    def with_iso_639_1(
        cls: Type[T],
        languages: List[T],
        iso_639_1: str,
        fallback: Optional[T]
    ) -> Optional[T]:

        for language in languages:
            if language.iso_639_1.lower() == iso_639_1.lower():
                return language
            continue
        return fallback

    @classmethod
    def derive_from_headers(
        cls: Type[T],
        available_languages: Optional[List[T]],
        headers: Headers,
        fallback_to: Optional[T] = None
    ) -> Optional[T]:

        if available_languages is None or len(available_languages) < 1:
            return fallback_to

        raw_value = headers.value_for(cls._ACCEPT_HEADER)
        accepted = AcceptLanguage.many_from_header(header=raw_value)
        priority_order = AcceptLanguage.in_priority_order(accepted)

        for acceptable_language in priority_order:
            candidate = cls.with_iso_639_1_and_variant(
                languages=available_languages,
                iso_639_1=acceptable_language.primary,
                variant_code=acceptable_language.variant,
                fallback=None
            )
            if candidate is not None:
                return candidate
            candidate = cls.with_iso_639_1(
                languages=available_languages,
                iso_639_1=acceptable_language.primary,
                fallback=None
            )
            if candidate is not None:
                return candidate
            continue

        return fallback_to
