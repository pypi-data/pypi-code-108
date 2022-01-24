import time
import logging
import json
from copy import deepcopy
import numpy as np
from ase.units import kB
from .constraints import CollectiveVariableConstraint

logger = logging.getLogger(__name__)


class NoneNotAcceptedError(Exception):
    pass


class PeakNotAcceptedError(Exception):
    pass


class MetaDynamicsSampler:
    """
    Class for performing meta dynamics sampler

    Parameters:

    mc: Montecarlo
        A Monte Carlo sampler

    bias: BiasPotential
        A bias potential that should be altered in order to recover the free
        energy

    flat_limit: float
        The histogram of visits is considered flat, when the minimum value
        is larger than flat_limit*np.mean(hist)

    mod_factor: float
        Modification factor in units of kB*T

    fname: str
        Filename used to store the simulation state when finished
    """

    def __init__(self, mc, bias, flat_limit=0.8, mod_factor=0.1, fname='metadyn.json'):
        self.mc = mc
        self.bias = bias
        self.mc.add_bias(self.bias)
        cnst = CollectiveVariableConstraint(xmin=self.bias.xmin,
                                            xmax=self.bias.xmax,
                                            getter=self.bias.getter)
        self.mc.generator.add_constraint(cnst)
        self.mc.update_current_energy()
        self.mc.attach(self.bias.getter, interval=1)
        self.visit_hist = deepcopy(bias)
        self.visit_hist.zero()
        self.flat_limit = flat_limit
        self.mod_factor = mod_factor * kB * self.mc.T
        self.log_freq = 30
        self.fname = fname
        self.progress_info = {'mean': 0.0, 'minimum': 0.0}
        self.observers = []
        self.quit = False

    def _getter_accepts_none(self):
        """Return True if the getter accepts None."""
        # TODO: Why is try-catch needed? Is it sufficient with ValueError?
        try:
            x = self.bias.getter(None)
            x = float(x)
        # pylint: disable=broad-except
        except Exception:
            return False
        return True

    def _getter_accepts_peak(self):
        """Return True if the getter supports the peak keyword."""
        # TODO: Why is try-catch needed? Is it sufficient with ValueError?
        try:
            x = self.bias.getter([], peak=True)
            x = float(x)
        # pylint: disable=broad-except
        except Exception:
            return False
        return True

    def add_observer(self, obs, interval=1):
        """Add observer.

        Parameters:

        obs: callable object
            A callable object that takes no arguments

        interval: int
            Will be called at even intervals given by this number
        """
        self.observers.append((obs, interval))

    def visit_is_flat(self):
        """Return True if the histogram of visits is flat."""
        i_min = self.visit_hist.get_index(self.visit_hist.xmin)
        i_max = self.visit_hist.get_index(self.visit_hist.xmax)
        coeff = self.visit_hist.get_coeff()[i_min:i_max]
        avg = np.mean(coeff)

        # Use min and not np.min. It looks like np.min behaves weird
        # when it is running on a worker thread
        minval = min(coeff.tolist())
        self.progress_info['mean'] = avg

        if avg > 0.0:
            self.progress_info['minval'] = minval / avg
        else:
            self.progress_info['minval'] = 0.0

        if np.max(avg) == 0:
            return False
        return minval > self.flat_limit * avg

    def update(self):
        """Update bias potential and visit histogram."""
        x = self.bias.getter(None)
        cur_value = self.bias.evaluate(x)
        self.bias.local_update(x, self.mod_factor)

        new_value = self.bias.evaluate(x)
        self.mc.current_energy += (new_value - cur_value)
        self.visit_hist.local_update(x, 1)

    def run(self, max_sweeps=None):
        """
        Run the calculation.

        Parameters:

        max_sweeps: int or None
            If given, the simulation terminates when this number of sweeps
            is reached
        """
        if not self._getter_accepts_none():
            raise NoneNotAcceptedError("Observer does not accept None as a system change")

        if not self._getter_accepts_peak():
            raise PeakNotAcceptedError(("Observer does not accept peak as a "
                                        "keyword argument to __call__"))

        if not hasattr(self.bias, 'get_coeff'):
            raise ValueError(('The bias potential needs to have a method ',
                              'called get_coeff(), which returns a histogram '
                              'representation of the bias potential'))

        if not hasattr(self.bias, 'local_update'):
            raise ValueError('The bias potential needs to have a method '
                             'called local_update(x, dE) which allows a local '
                             'update at position x')
        conv = False
        now = time.time()

        sweep_no = 0
        counter = 0
        logger.info("Starting metadynamics sampling...")
        logger.info("Writing result to %s every %s sec", self.fname, self.log_freq)
        self.mc.initialize_run()
        while not conv:
            counter += 1
            if time.time() - now > self.log_freq:
                msg = f"Sweep no. {int(counter/len(self.mc.atoms))} "
                msg += f"Average visits: {self.progress_info['mean']:.2e}. "
                msg += f"Min/avg: {self.progress_info['minval']:.2e} "
                msg += f"x: {self.bias.getter(None):.2e}"
                logger.info(msg)
                self.save()
                now = time.time()

            # pylint: disable=protected-access
            self.mc._mc_step()
            self.update()
            if self.visit_is_flat():
                conv = True

            sweep_no = int(counter / len(self.mc.atoms))

            if max_sweeps is not None:
                if sweep_no > max_sweeps:
                    logger.info('Reached max number of sweeps...')
                    conv = True

            for obs, interval in self.observers:
                if counter % (interval * len(self.mc.atoms)) == 0:
                    obs()

            if self.quit:
                break

        logger.info("Results from metadynamics sampling written to %s", self.fname)
        self.save()

    def save(self):
        """Save the free energy result to a file."""
        pot = self.bias.todict()
        xmin = self.bias.xmin
        xmax = self.bias.xmax
        x = np.linspace(xmin, xmax, 200)
        beta = 1.0 / (kB * self.mc.T)
        betaG = [self.bias.evaluate(y) * beta for y in x]
        data = {'bias_pot': pot, 'betaG': {'x': x.tolist(), 'y': betaG}}
        with open(self.fname, 'w') as out:
            json.dump(data, out)
