import numpy as np
from .mc_observer import MCObserver


class SiteOrderParameter(MCObserver):
    """
    Detect phase transitions by monitoring the average number of sites that
    are occupied by a different element from the initial structure. This
    observer has to be executed on every MC step.

    Parameters:

    atoms: Atoms object
        Atoms object use for Monte Carlo
    """

    name = "SiteOrderParameter"

    def __init__(self, atoms):
        super().__init__()
        self.atoms = atoms
        self.orig_nums = self.atoms.get_atomic_numbers()
        self.avg_num_changed = 0
        self.avg_num_changed_sq = 0
        self.num_calls = 0
        self.current_num_changed = 0
        self.site_changed = np.zeros(len(self.atoms), dtype=np.uint8)

    def _check_all_sites(self):
        """Check if symbols have changed on all sites."""
        nums = self.atoms.get_atomic_numbers()
        self.current_num_changed = np.count_nonzero(nums != self.orig_nums)
        self.site_changed = (nums != self.orig_nums)

    def reset(self):
        """Resets the tracked data. (Not the original symbols array)."""
        self.avg_num_changed = 0
        self.avg_num_changed_sq = 0
        self.num_calls = 0
        self.current_num_changed = 0
        self._check_all_sites()

    def __call__(self, system_changes):
        """Get a new value for the order parameter.

        system_changes: list
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """

        self.num_calls += 1
        assert self.current_num_changed < len(self.atoms)

        # The point this function is called the atoms object is already
        # updated
        for change in system_changes:
            indx = change[0]
            if self.site_changed[indx]:
                if self.atoms[indx].number == self.orig_nums[indx]:
                    self.current_num_changed -= 1
                    self.site_changed[indx] = False
            else:
                if self.atoms[indx].number != self.orig_nums[indx]:
                    self.current_num_changed += 1
                    self.site_changed[indx] = True
        self.avg_num_changed += self.current_num_changed
        self.avg_num_changed_sq += self.current_num_changed**2

    def get_averages(self):
        """
        Get the average and standard deviation of the number of sites that
        are different from the initial state.
        """
        average = float(self.avg_num_changed) / self.num_calls
        average_sq = float(self.avg_num_changed_sq) / self.num_calls
        var = average_sq - average**2

        # If variance is close to zero it can in some cases by
        # slightly negative. Add a safety check for this
        var = max(var, 0.0)
        return {"site_order_average": average, "site_order_std": np.sqrt(var)}

    def interval_ok(self, interval):
        return interval == 1
