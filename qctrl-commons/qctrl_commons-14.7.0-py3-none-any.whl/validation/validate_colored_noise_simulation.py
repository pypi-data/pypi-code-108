"""
Validator for core__calculateColoredNoiseSimulation mutation.
"""
import numpy as np

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.serializers import decode
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.messages import Messages
from qctrlcommons.validation.utils import (
    check_drives_drifts_shifts,
    check_initial_state_vector,
    check_sample_times,
    check_target,
    read_numpy_array,
)


class CalculateColoredNoiseSimulationValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateColoredNoiseSimulation mutation.
    """

    properties = {"duration": {"type": "number", "exclusiveMinimum": 0}}

    def check_trajectory_count(self, input_):  # pylint:disable=no-self-use
        """
        Expect trajectory count >=1 if provided.

        Parameters
        ----------
        input_: dict
            the GraphQL input.

        Raises
        -------
        QctrlFieldError
            Validation check failed.
        """
        trajectory_count = input_.get("trajectoryCount")
        if trajectory_count is not None and trajectory_count < 1:
            raise QctrlFieldError(
                message=Messages(field_name="trajectoryCount", minimum=1).minimum,
                fields=["trajectoryCount"],
            )

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

    def check_noise_in_drive_shift_drift(
        self, input_: dict
    ):  # pylint:disable=no-self-use
        """
        Expect for each ColoredSimulationNoise (there can be several, since
        each drive, shift and drift can optionally have one)

        - frequency_step>0
        - time_domain_samples_count>0
        - all power_densities>=0

        Parameters
        ----------
        input_: dict
            the GraphQL input.

        Raises
        -------
        QctrlFieldError
            Validation check failed.
        """
        items = (
            (input_.get("drives") or [])
            + (input_.get("shifts") or [])
            + (input_.get("drifts") or [])
        )

        for item in items:
            noise = item.get("noise")
            if noise:
                if noise["frequencyStep"] <= 0:
                    raise QctrlFieldError(
                        message="frequencyStep must be greater than 0",
                        fields=["frequencyStep"],
                    )

                if noise["timeDomainSampleCount"] <= 0:
                    raise QctrlFieldError(
                        message="timeDomainSampleCount must be greater than 0",
                        fields=["timeDomainSampleCount"],
                    )

                power_densities: np.ndarray = decode(noise["powerDensities"])
                if min(power_densities) < 0:
                    raise QctrlFieldError(
                        message="all powerDensities must be greater than or equal to 0",
                        fields=["powerDensities"],
                    )
