"""
Validator for core__calculateQuasiStaticScan mutation.
"""

import numpy as np

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.utils import (
    check_drives_drifts_shifts,
    check_target,
    read_numpy_array,
)

MAX_SAMPLE_COUNT = 8192


class CalculateQuasiStaticScanValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateQuasiStaticScan mutation.
    """

    # pylint:disable=no-self-use

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

        check_target(read_numpy_array(**input_["target"]["operator"]))

    def check_at_least_one_noise(self, input_: dict) -> None:
        """
        Checks that the controls have at least one noise.

        Parameters
        ----------
        input_: dict
            the serialized input

        Raises
        -------
        QctrlFieldError
            if validation check failed.
        """
        items = (
            (input_.get("drives") or [])
            + (input_.get("shifts") or [])
            + (input_.get("drifts") or [])
        )
        for item in items:
            if item.get("noise"):
                return
        raise QctrlFieldError(
            message="""
            At least one of the drives, shifts, and drifts must have a noise field.
            """,
            fields=["noise"],
        )

    def check_noise_values_lengths(self, input_: dict) -> None:
        """
        The product of the lengths of the values arrays of all the noises
        is less than or equal to MAX_SAMPLE_COUNT.

        Parameters
        ----------
        input_: dict
            the dictionary representing the quasi static scan input

        Raises
        -------
        QctrlFieldError
            validation check failed
        """

        noise_values_length = np.prod(
            [
                len(control["noise"]["values"])
                for control in (input_.get("drives") or [])
                + (input_.get("shifts") or [])
                + (input_.get("drifts") or [])
                if control.get("noise")
            ]
        )

        if noise_values_length > MAX_SAMPLE_COUNT:
            raise QctrlFieldError(
                message="The product of the lengths of the values arrays of all the noises "
                f"must be less than or equal to {MAX_SAMPLE_COUNT}.",
                fields=["noise"],
            )
