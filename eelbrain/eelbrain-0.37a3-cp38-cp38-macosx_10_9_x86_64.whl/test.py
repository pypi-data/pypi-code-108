"""Some basic statistical tests for univariate data."""
__test__ = False
from ._stats.glm import ANOVA
from ._stats.test import (
    Correlation,
    TTestOneSample, TTestIndependent, TTestRelated, MannWhitneyU, WilcoxonSignedRank,
    pairwise, ttest, correlations,
    bootstrap_pairwise, lilliefors,
    pairwise_correlations,
)
