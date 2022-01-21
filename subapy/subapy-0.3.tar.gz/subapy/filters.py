from __future__ import annotations

__all__ = (
    'Filter'
)

class Filter:
    """
    This class is used to add (a) filter(s) to a query.
    Example: Select rows that has a age value greater than equals to 18.
    Code: Filter('age', 'gte', '18')
    """
    def __init__(self, col: str, op: str, q: str):
        self.col = col
        self.op = op
        self.q = q
        supported_filters = ['eq', 'gt', 'gte','lt', 'lte', 'neq', 'in', 'is', 'fts']
        if op not in supported_filters:
            raise Exception(f"Filter not supported: {op}")
        self.filter = f"{op}.{q}"

    def to_dict(self):
        return {self.col:f"{self.op}.{self.q}"}
