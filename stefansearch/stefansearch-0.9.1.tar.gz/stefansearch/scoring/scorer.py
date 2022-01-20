import abc
import typing
import dataclasses as dc


@dc.dataclass
class TermScoreInfo:
    """
    Data used to calculate a score for a single term of a query.
    TODO: IMPROVE VARIABLE NAMES
    """
    # The actual term being scored
    term: str
    # Frequency of the term in the query
    qf: int
    # Frequency of the term in the document
    df: int
    # Frequency of the term in the corpus
    cf: int
    # Number of documents in the corpus that contain the term
    nd: int
    # Number of documents in the corpus
    nc: int
    # Number of terms in the document
    dl: int
    # Number of terms in the corpus
    dc: int
    # Average number of terms in a document
    avdl: float


@dc.dataclass
class DocScoreInfo:
    """Data used to calculate the score of a document."""
    terms: typing.List[TermScoreInfo]


class Scorer(abc.ABC):
    """
    Base class used to implement a scorer that scores documents.

    A `Scorer` implementation must implement the `calc_score()` function.
    """
    @abc.abstractmethod
    def calc_score(self, info: DocScoreInfo) -> float:
        """Calculate and return score for a `DocScoreInfo` instance."""
        pass

    @abc.abstractmethod
    def to_sortable(self, score: float) -> float:
        """
        Transform a score calculated by this Scorer into a value
        that can be sorted numerically from high to low (higher score =
        better).

        For example, if the implementation calculates negative scores,
        the `to_sortable()` method should provide the absolute value.
        """
        pass
