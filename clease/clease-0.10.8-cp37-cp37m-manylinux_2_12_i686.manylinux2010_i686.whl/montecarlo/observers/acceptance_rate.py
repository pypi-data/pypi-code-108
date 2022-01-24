from typing import Sequence, Dict
from clease.datastructures import SystemChange
from clease.montecarlo.observers.mc_observer import MCObserver

__all__ = ('AcceptanceRate',)


class AcceptanceRate(MCObserver):
    """
    Observer that tracks the fraction of monte carlo steps that is accepted
    """

    def __init__(self):
        super().__init__()
        self.num_calls = 0
        self.num_accept = 0

    @property
    def rate(self) -> float:
        """
        Acceptance rate
        """
        if self.num_calls == 0:
            return 0.0
        return self.num_accept / self.num_calls

    def reset(self):
        """
        Reset the observer
        """
        self.num_calls = 0
        self.num_accept = 0

    def __call__(self, system_changes: Sequence[SystemChange]) -> None:
        """
        Updates the acceptance rate.

        :param system_changes: Sequence with introduces changes. A move is considered
            accepted if old_symb != new_symb in any of the changes
        """
        accepted = any(c.old_symb != c.new_symb for c in system_changes)

        if accepted:
            self.num_accept += 1
        self.num_calls += 1

    def get_averages(self) -> Dict[str, float]:
        """
        Return dictionary with the rate such that it is added to thermodynaic quantities
        """
        return {'accept_rate': self.rate}
