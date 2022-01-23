"""
Nozomi
Accept Language Module
author: hugh@blinkybeach.com
"""
from typing import TypeVar, Type, Optional, Tuple, List
from nozomi.ancillary.immutable import Immutable
from nozomi.http.headers import Headers

T = TypeVar('T', bound='AcceptLanguage')


class AcceptLanguage:

    def __init__(
        self,
        primary: str,
        variant: Optional[str] = None,
        q_value: Optional[float] = None
    ) -> None:

        if q_value is None:
            q_value = 1.0
        self._q_value = q_value
        self._variant = variant
        self._primary = primary

        return

    primary = Immutable(lambda s: s._primary.lower())
    variant = Immutable(lambda s: s._variant)

    @classmethod
    def from_headers(cls: Type[T], headers: Headers) -> Optional[T]:
        raw = headers.get('accept-language')
        if raw is None:
            return None

        return cls.from_header_item(raw)

    @classmethod
    def from_header_item(cls: Type[T], string: str) -> Optional[T]:
        'en-GB,en-US;q=0.9,en;q=0.8'
        if len(string) < 1:
            return None

        if '-' not in string and ';' not in string:
            return cls(primary=string)

        def extract_q_value(q_statement: str) -> Optional[float]:
            if 'q=' not in q_statement:
                return None
            q_candidates = [c for c in q_statement.split('=') if c != '']
            if len(q_candidates) < 2:
                return None
            q_value: Optional[float] = None
            try:
                q_value = float(q_candidates[1])
            except Exception:
                return None
            return q_value

        if '-' not in string:
            pieces = [p for p in string.split(';') if p != '']
            primary = pieces[0]
            if len(pieces) < 2:
                return cls(primary=primary)
            q_value = extract_q_value(pieces[1])
            return cls(primary=primary, q_value=q_value)

        def extract_lang(string: str) -> Tuple[str, Optional[str]]:
            pieces = [c for c in string.split('-') if c != '']
            if len(pieces) < 2:
                return pieces[0], None
            return pieces[0], pieces[1]

        components = string.split(';')
        if components[0] == '':
            return None

        real_components = [s for s in components if s != '']

        primary, variant = extract_lang(real_components[0])

        if len(real_components) < 2:
            return cls(
                primary=primary,
                variant=variant
            )

        return cls(
            primary=primary,
            variant=variant,
            q_value=extract_q_value(q_statement=real_components[1])
        )

    @classmethod
    def many_from_header(cls: Type[T], header: str) -> List[T]:
        items = header.split(',')
        parsed_items = [cls.from_header_item(i) for i in items]
        return [a for a in parsed_items if a is not None]

    @classmethod
    def with_highest_priority(cls: Type[T], items: List[T]) -> Optional[T]:
        if len(items) < 1:
            return None
        return items.sort(key=lambda i: i._q_value, reverse=True)[0]

    @classmethod
    def in_priority_order(cls: Type[T], items: List[T]) -> Optional[T]:
        return sorted(items, key=lambda i: i._q_value, reverse=True)

    def __repr__(self) -> str:
        identity = self.primary
        if self.variant is not None:
            identity += '-' + self.variant
        identity += '; ' + str(self._q_value)
        return 'Accept Language: ' + identity
