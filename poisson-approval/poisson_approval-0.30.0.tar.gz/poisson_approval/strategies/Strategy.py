from copy import deepcopy
from poisson_approval.constants.basic_constants import *
from poisson_approval.utils.SuperclassMeta import SuperclassMeta
from poisson_approval.utils.UtilCache import cached_property, DeleteCacheMixin, property_deleting_cache


class Strategy(DeleteCacheMixin, metaclass=SuperclassMeta):
    """A strategy profile (abstract class).

    Parameters
    ----------
    profile : Profile, optional
        The "context" in which the strategy is used.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.
    """

    def __init__(self, profile=None, voting_rule=None):
        self.profile = profile  # Store the profile (if any)
        self.voting_rule = self._get_voting_rule_(profile, voting_rule)

    profile = property_deleting_cache('_profile')
    voting_rule = property_deleting_cache('_voting_rule')

    @staticmethod
    def _get_voting_rule_(profile, voting_rule):
        if voting_rule is None:
            if profile is not None:
                return profile.voting_rule
            else:
                return APPROVAL
        return voting_rule

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')

    def deepcopy_with_attached_profile(self, profile):
        """Deep copy with an attached profile.

        Parameters
        ----------
        profile : Profile
            The new attached profile.

        Returns
        -------
        Strategy
            A deep copy of this strategy, with `profile` attached to it.
        """
        strategy = deepcopy(self)
        strategy.profile = profile
        strategy.voting_rule = profile.voting_rule
        return strategy

    # Additional stuff when a profile is given
    # For tests of this, see file ``test_strategy_embed_profile.py``.

    @cached_property
    def is_equilibrium(self):
        """EquilibriumStatus : Whether this strategy is an equilibrium (in the context of the given profile). Cf.
        :meth:`Profile.is_equilibrium`.
        """
        if self.profile is not None:
            return self.profile.is_equilibrium(self)

    @cached_property
    def tau(self):
        """TauVector : The tau-vector associated to this strategy (in the context of the given profile). Cf.
        :meth:`Profile.tau`.
        """
        if self.profile is not None:
            return self.profile.tau(self)

    # noinspection NonAsciiCharacters
    @property
    def τ(self):
        """TauVector : The tau-vector (alternate notation). Cf. :meth:`Profile.τ`.
        """
        return self.tau

    @cached_property
    def share_sincere(self):
        """Number: Share of voters that happen to cast a sincere ballot (in the context of the given profile).

        Cf. :meth:`ProfileCardinal.share_sincere`. This is defined only for a :class:`ProfileCardinal`.
        """
        if self.profile is not None:
            try:
                return self.profile.share_sincere(self)
            except AttributeError:
                return

    @cached_property
    def share_sincere_among_strategic_voters(self):
        """Number: Share of strategic voters that happen to cast a sincere ballot (in the context of the given profile).

        Cf. :meth:`ProfileCardinal.share_sincere_among_strategic_voters`. This is defined only for a
        :class:`ProfileCardinal`.
        """
        if self.profile is not None:
            try:
                return self.profile.share_sincere_among_strategic_voters(self)
            except AttributeError:
                return


def make_method(name):
    def _method(self):
        if self.tau is not None:
            return getattr(self.tau, name)()
    _method.__doc__ = "Defined when a profile is given. Cf. :meth:`TauVector.%s`." % name
    return _method


for my_method in ['print_weak_pivots', 'print_all_pivots']:
    setattr(Strategy, my_method, make_method(my_method))


def make_property(name, doc):
    def _property(self):
        if self.tau is not None:
            return getattr(self.tau, name)
    _property.__doc__ = "Defined when a profile is given. Cf. :attr:`TauVector.%s`." % name
    return property(_property)


for my_property, my_doc in [('scores', 'The scores.'),
                            ('winners', 'The winners.'),
                            ('trio', 'Event: trio.'),
                            ('d_ranking_best_response', 'Best response profile.'),
                            ('share_single_votes', 'Share of single votes in tau (incl. fanatic and sincere voters).'),
                            ('share_double_votes', 'Share of double votes in tau (incl. fanatic and sincere voters).')]:
    setattr(Strategy, my_property, make_property(my_property, my_doc))

for my_property, my_doc in [
        ('trio_1t_', 'Event: trio of type 1t (this candidate has one point less than the other two.')]:
    for candidate in CANDIDATES:
        my_property_full = my_property + candidate
        setattr(Strategy, my_property_full, make_property(my_property_full, my_doc))

for my_property, my_doc in [
        ('duo_', 'Event: duo.'),
        ('pivot_weak_', 'Event: weak pivot.'),
        ('pivot_strict_', 'Event: strict pivot.'),
        ('trio_2t_', 'Event: trio of type 2t (these two candidates have one point less than the other one).')]:
    for pair in PAIRS_WITH_INVERSIONS:
        my_property_full = my_property + pair
        setattr(Strategy, my_property_full, make_property(my_property_full, my_doc))

for my_property, my_doc in [('pivot_tij_', 'Event: `personalized pivot` of type Tij.'),
                            ('pivot_tjk_', 'Event: `personalized pivot` of type Tjk.')]:
    for ranking in RANKINGS:
        my_property_full = my_property + ranking
        setattr(Strategy, my_property_full, make_property(my_property_full, my_doc))
