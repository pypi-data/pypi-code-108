from collections.abc import Iterable, Iterator


class Filter:
    # allows filter chain selection
    def __init__(self, filter: Iterable[bool]):
        self.filter = filter

    def __repr__(self) -> str:
        return f'Filter({", ".join([str(x) for x in self.filter])})'

    def __and__(self, other) -> Iterable[bool]:
        return Filter([x and y for x, y in zip(self.filter, other)])

    def __or__(self, other) -> Iterable[bool]:
        return Filter([x or y for x, y in zip(self.filter, other)])

    def __len__(self) -> int:
        return len(self.filter)
    
    def __getitem__(self, key) -> bool:
        return self.filter[key]

    def __iter__(self) -> Iterator:
        return iter(self.filter)