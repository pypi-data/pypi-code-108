import dataclasses as dc
# TODO: BETTER NAME/ORGANIZATION FOR THIS FILE. PROBABLY TEMPORARY


@dc.dataclass
class IntermediateResult:
    """Stores the score that a specified `doc_id` received."""
    doc_id: int
    score: float
    sortable_score: float

    def __lt__(self, other: 'IntermediateResult'):
        return self.sortable_score < other.sortable_score


@dc.dataclass
class DocInfo:
    """Store some metainformation for an indexed document."""
    slug: str
    num_terms: int
