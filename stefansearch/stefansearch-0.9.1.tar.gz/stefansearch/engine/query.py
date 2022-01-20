import dataclasses as dc
import typing


@dc.dataclass
class ProcessedQuery:
    query: str
    terms: typing.List[str]
    term_counts: typing.Dict[str, int]
