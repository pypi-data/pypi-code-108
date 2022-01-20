import math
from stefansearch.scoring.scorer import Scorer, DocScoreInfo, TermScoreInfo


class Bm25Scorer(Scorer):

    def __init__(
            self,
            k1: float = 1.2,
            k2: float = 100,
            b: float = 0.75,
    ):
        """
        BM-25 scoring.

        k1, k2, and b are tuning parameters.
        """
        self.k1 = k1
        self.k2 = k2
        self.b = b

    def calc_score(self, info: DocScoreInfo) -> float:
        return sum([self._calc_single_term(t) for t in info.terms])

    def to_sortable(self, score: float) -> float:
        return -score

    def _calc_single_term(self, info: TermScoreInfo) -> float:
        K = self.k1 * ((1 - self.b) + self.b * info.dl / info.avdl)
        return (
                math.log10(1 / ((info.nd + 0.5) / (info.nc - info.nd + 0.5))) *
                (((self.k1 + 1) * info.df) / (K + info.df)) *
                (((self.k2 + 1) * info.qf) / (self.k2 + info.qf))
        )
