from poisson_approval.utils.ComputationEngineSymbolic import ComputationEngineSymbolic
from poisson_approval.utils.ComputationEngineNumeric import ComputationEngineNumeric


def computation_engine(symbolic):
    """Choose the computation engine.

    Parameters
    ----------
    symbolic : bool
        Whether symbolic computation should be activated.

    Returns
    -------
    ComputationEngine
        :class:`ComputationEngineSymbolic` if `symbolic` is True, :class:`ComputationEngineNumeric` otherwise.
    """
    return ComputationEngineSymbolic if symbolic else ComputationEngineNumeric
