from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.tau_vector.TauVector import TauVector
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.utils.UtilBallots import allowed_ballots


class RandTauVectorGridUniform(RandSimplexGridUniform):
    """A random factory of tau-vectors (:class:`TauVector`), uniform on a grid.

    Parameters
    ----------
    denominator : int
        The grain of the grid.
    ballots : iterable, optional
        These ballots (e.g. ``'a'``, ``'ab'``) will have a variable share. Default: all allowed ballots.
    d_ballot_fixed_share : dict, optional
        A dictionary. For each entry ``ballot: fixed_share``, this ballot will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        These additional arguments will be passed directly to :class:`TauVector`.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_tau = RandTauVectorGridUniform(denominator=7)
        >>> tau = rand_tau()
        >>> print(tau)
        <a: 2/7, ab: 1/7, ac: 1/7, b: 3/7> ==> a, b

    If the voting rule is not approval, only the relevant ballots are used:

        >>> initialize_random_seeds()
        >>> rand_tau = RandTauVectorGridUniform(denominator=7, voting_rule=PLURALITY)
        >>> tau = rand_tau()
        >>> print(tau)
        <a: 2/7, b: 4/7, c: 1/7> ==> b (Plurality)

    Using the optional parameters:

        >>> from fractions import Fraction
        >>> rand_tau = RandTauVectorGridUniform(
        ...     denominator=5,
        ...     ballots=['b', 'bc'], d_ballot_fixed_share={'a': Fraction(2, 7)},
        ...     symbolic=True)
        >>> tau = rand_tau()
        >>> print(tau)
        <a: 2/7, b: 1/7, bc: 4/7> ==> b

    For more examples, cf. :class:`RandSimplexGridUniform`.
    """

    def __init__(self, denominator, ballots=None, d_ballot_fixed_share=None, **kwargs):
        if ballots is None:
            try:
                ballots = allowed_ballots(kwargs['voting_rule'])
            except KeyError:
                ballots = allowed_ballots()
        super().__init__(cls=TauVector, denominator=denominator, keys=ballots,
                         d_key_fixed_share=d_ballot_fixed_share, **kwargs)
