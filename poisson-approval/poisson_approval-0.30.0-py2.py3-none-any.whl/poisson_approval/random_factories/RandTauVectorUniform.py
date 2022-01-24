from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.tau_vector.TauVector import TauVector
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.utils.UtilBallots import allowed_ballots


class RandTauVectorUniform(RandSimplexUniform):
    """A random factory of tau-vectors (:class:`TauVector`) following the uniform distribution.

    Parameters
    ----------
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
        >>> rand_tau = RandTauVectorUniform()
        >>> tau = rand_tau()
        >>> print(tau)
        <a: 0.4236547993389047, ab: 0.12122838365799216, ac: 0.0039303209304278885, b: 0.05394987214431912, \
bc: 0.1124259903007756, c: 0.2848106336275805> ==> a

    If the voting rule is not approval, only the relevant ballots are used:

        >>> initialize_random_seeds()
        >>> rand_tau = RandTauVectorUniform(voting_rule=PLURALITY)
        >>> tau = rand_tau()
        >>> print(tau)
        <a: 0.5488135039273248, b: 0.16637586244509472, c: 0.2848106336275805> ==> a (Plurality)

    Using the optional parameters:

        >>> rand_tau = RandTauVectorUniform(
        ...     ballots=['b', 'bc'], d_ballot_fixed_share={'a': 0.5},
        ...     symbolic=True)
        >>> tau = rand_tau()
        >>> print(tau)
        <a: 0.5, b: 0.30138168803582194, bc: 0.19861831196417806> ==> a, b

    For more examples, cf. :class:`RandSimplexUniform`.
    """

    def __init__(self, ballots=None, d_ballot_fixed_share=None, **kwargs):
        if ballots is None:
            try:
                ballots = allowed_ballots(kwargs['voting_rule'])
            except KeyError:
                ballots = allowed_ballots()
        super().__init__(cls=TauVector, keys=ballots, d_key_fixed_share=d_ballot_fixed_share, **kwargs)
