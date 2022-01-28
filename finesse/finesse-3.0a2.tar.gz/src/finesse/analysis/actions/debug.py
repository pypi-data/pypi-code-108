from ...solutions import BaseSolution
from .base import Action
import textwrap


class Debug(Action):
    """An action that will start an IPython debug shell."""

    def __init__(self, name="Debug"):
        super().__init__(name)
        self.cancel = False

    def _requests(self, model, memo, first=True):
        pass

    def do(self, state):
        if not self.cancel:
            from IPython.terminal.embed import InteractiveShellEmbed

            banner = textwrap.dedent(
                f"""
            ---- Finesse Debugging
            Instance          : {self.name}

            To stop future debug calls set : self.cancel = True
            To continue analyis            : exit
            """
            )
            self.shell = InteractiveShellEmbed(banner1=banner)
            self.shell()


class SaveMatrixSolution(BaseSolution):
    """
    Attributes
    ----------
    carrier : coo_matrix
        A Scipy coo_matrix of the carrier simulation matrix. None if the matrix was not
        available.
    signal : coo_matrix
        A Scipy coo_matrix of the signal simulation matrix. None if the matrix was not
        available.
    """

    pass


class SaveMatrix(Action):
    """An action that will save the current state of the matrix being used by the
    simulation.

    Not something that should be used lightly in loops or multiple times in a large
    simulation. Using this in something like a full LIGO model with many HOMs and
    sidebands will quickly fill up memory.
    """

    def __init__(self, *, name="savematrix"):
        super().__init__(name)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        from scipy.sparse import coo_matrix

        sim = state.sim
        sol = SaveMatrixSolution(self.name)
        if sim.carrier is not None:
            data, rows, cols = sim.carrier.M().get_matrix_elements()
            sol.carrier = coo_matrix((data, (rows, cols)))
        else:
            sol.carrier = None

        if sim.signal is not None:
            data, rows, cols = sim.signal.M().get_matrix_elements()
            sol.signal = coo_matrix((data, (rows, cols)))
        else:
            sol.signal = None
        return sol
