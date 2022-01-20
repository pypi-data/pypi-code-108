"""
Validator for core__calculateCoherentSimulation mutation.
"""

from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.utils import (
    check_drives_drifts_shifts,
    check_initial_state_vector,
    check_sample_times,
    check_target,
    read_numpy_array,
)


class CalculateCoherentSimulationValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateCoherentSimulation mutation.
    """

    properties = {"duration": {"type": "number", "exclusiveMinimum": 0}}

    def check_input_hamiltonian(self, input_: dict):  # pylint:disable=no-self-use
        """
        Check Hamiltonian that is formatted as the sum of drives, drifts, and shifts.

        Following checks are performed in order:

        1. check there must be at least one of drives, drifts, or shifts.

        2. check the operator type for Hamiltonian terms:

            drive: must have non Hermitian operator
            shift: must have Hermitian operator
            drift: must have Hermitian operator

        3. check control segment durations

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """

        check_drives_drifts_shifts(
            input_["duration"],
            input_.get("drives"),
            input_.get("drifts"),
            input_.get("shifts"),
        )

    def check_input_sample_times(self, input_: dict):  # pylint:disable=no-self-use
        """
        If provided, sample times should be in order, and within [0, duration].

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """

        if input_.get("sampleTimes") is not None:
            check_sample_times(input_["sampleTimes"], input_["duration"])

    def check_initial_state_vector(self, input_: dict):  # pylint:disable=no-self-use
        """
        If provided, initial state vector must be normalized.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """

        if input_.get("initialStateVector") is not None:
            check_initial_state_vector(read_numpy_array(**input_["initialStateVector"]))

    def check_input_target(self, input_: dict):  # pylint:disable=no-self-use
        """
        If provided, target must be a partial isometry.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """

        if input_.get("target") is not None:
            check_target(read_numpy_array(**input_["target"]["operator"]))
