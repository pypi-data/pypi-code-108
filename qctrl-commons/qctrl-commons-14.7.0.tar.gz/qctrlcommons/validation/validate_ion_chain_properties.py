"""
Validator for core__calculateIonChainProperties mutation.
"""
import numpy as np

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.messages import Messages


class CalculateIonChainPropertiesValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateIonChainProperties mutation.
    """

    properties = {"ionCount": {"type": "number", "minimum": 1}}

    # pylint:disable=no-self-use
    def check_atomic_mass(self, input_):
        """
        Check The atomic mass must be greater than zero,
        taking into account rounding errors

        Raises
        ------
        QctrlFieldError
            if atomic mass is less than or equal to 0
        """
        atomic_mass = input_.get("atomicMass")
        if np.isclose(atomic_mass, 0) or atomic_mass <= 0:
            raise QctrlFieldError(
                Messages(field_name="atomicMass", minimum=0).greater_than,
                ["atomicMass"],
            )

    def check_center_of_mass_frequencies(self, input_):
        """
        The center of mass frequencies must be greater than zero,
        taking into account floating point rounding errors

        Raises
        ------
        QctrlFieldError
            if any center_of_mass_frequencies is less than or equal to 0
        """
        center_of_mass_frequency_dict = {
            "radialXCenterOfMassFrequency": input_.get("radialXCenterOfMassFrequency"),
            "radialYCenterOfMassFrequency": input_.get("radialYCenterOfMassFrequency"),
            "axialCenterOfMassFrequency": input_.get("axialCenterOfMassFrequency"),
        }

        for var_name, value in center_of_mass_frequency_dict.items():
            if np.isclose(value, 0) or value <= 0:
                raise QctrlFieldError(
                    Messages(field_name=var_name, minimum=0).greater_than, [var_name]
                )

    def check_wave_number(self, input_):
        """
        At least one of the wave numbers must be different than zero,
        taking into account floating point rounding errors

        Raises
        -------
        QctrlFieldError
            if all wave numbers are less than or equal to 0
        """

        radial_x_wave_number = input_.get("radialXWaveNumber")
        radial_y_wave_number = input_.get("radialYWaveNumber")
        axial_wave_number = input_.get("axialWaveNumber")

        if np.allclose(
            np.array([radial_x_wave_number, radial_y_wave_number, axial_wave_number]), 0
        ):
            raise QctrlFieldError(
                "At least one of the wave numbers must be different than zero",
                ["radialXWaveNumber", "radialWaveNumber", "axialWaveNumber"],
            )

    # pylint:enable=no-self-use
