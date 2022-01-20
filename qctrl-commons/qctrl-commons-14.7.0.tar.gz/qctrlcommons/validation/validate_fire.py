"""
Validator for core__calculateFire mutation.
"""
import re

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator


class CalculateFireValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateFire mutation.
    """

    _QASM_PATTERN_RE = re.compile(r"OPENQASM 2\.0\;")

    properties = {
        "circuits": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "shotCount": {"type": "number", "exclusiveMinimum": 0},
    }

    def check_qasm_circuit_format(self, input_: dict):  # pylint:disable=no-self-use
        """
        Expect all circuits are valid QASM circuit strings.

        Parameters
        ----------
        input_ : dict
            the GraphQL input.
        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        for index, circuit in enumerate(input_.get("circuits", [])):
            if not self._QASM_PATTERN_RE.match(circuit):
                raise QctrlFieldError(
                    message=f"Item {index} is not in valid QASM format.",
                    fields=["circuits"],
                )
