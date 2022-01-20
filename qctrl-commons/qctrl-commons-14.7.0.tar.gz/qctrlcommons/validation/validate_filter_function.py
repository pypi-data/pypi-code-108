"""
Validator for core__calculateFilterFunction mutation.
"""
import numpy as np

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.utils import (
    check_drives_drifts_shifts,
    read_numpy_array,
)


class CalculateFilterFunctionValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateFilterFunction mutation.
    """

    properties = {
        "duration": {"type": "number", "exclusiveMinimum": 0},
        "sampleCount": {"type": ["number", "null"], "exclusiveMinimum": 0},
    }

    def check_drive_or_shift(self, input_: dict):  # pylint:disable=no-self-use
        """
        Expect at least one drive or shift is provided.

        Parameters
        ----------
        input_ : dict
            the GraphQL input.
        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        if not (input_.get("drives") or input_.get("shifts")):
            raise QctrlFieldError(
                message="Must have at least one drive or shift",
                fields=["drives", "shifts"],
            )

    def check_input_hamiltonian(self, input_: dict):  # pylint:disable=no-self-use
        """
        Check Hamiltonian that is formatted as the sum of drives, drifts, and shifts.

        Following checks are performed in order:

        1. check there must be at least one of drives or shifts.

        2. check the operator type for Hamiltonian terms:

            drive: must have non Hermitian operator
            shift: must have Hermitian operator

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
            input_.get("drift"),
            input_.get("shifts"),
        )

    def check_projection(self, input_: dict):  # pylint:disable=no-self-use
        """
        If provided, projection operator should be Hermitian and idempotent.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        if input_.get("projectionOperator") is not None:
            projector = read_numpy_array(**input_["projectionOperator"])
            if len(projector.shape) != 2 or projector.shape[0] != projector.shape[1]:
                raise QctrlFieldError(
                    message="Projector operator must be a 2D array, "
                    f"got {projector} instead",
                    fields=["projectorOperator"],
                )

            if not np.allclose(projector, projector.T.conj()) or not np.allclose(
                projector.dot(projector), projector
            ):
                raise QctrlFieldError(
                    message="Projector operator must be Hermitian and idempotent, "
                    f"got {projector} instead",
                    fields=["projectorOperator"],
                )

    def check_single_noise(self, input_: dict):  # pylint:disable=no-self-use
        """
        Expect that exactly one drift/shift/drive has a noise flag set to true.

        Parameters
        ----------
        input_ : dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        noises_found = 0

        items = [
            *(input_.get("drives") or []),
            *(input_.get("shifts") or []),
            *(input_.get("drifts") or []),
        ]

        for item in items:
            if item.get("noise"):
                noises_found += 1

                if noises_found > 1:
                    break

        if noises_found != 1:
            raise QctrlFieldError(
                message="Exactly one drive, shift or drift must be noise.",
                fields=["drives", "shifts", "drifts"],
            )
