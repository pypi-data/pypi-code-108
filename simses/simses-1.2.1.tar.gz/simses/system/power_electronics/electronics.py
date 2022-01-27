import numpy as np

from simses.commons.log import Logger
from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter


class PowerElectronics:
    """ class to update the power elections values"""

    def __init__(self, acdc_converter: AcDcConverter):
        self.__log: Logger = Logger(type(self).__name__)
        self.__acdc_converter: AcDcConverter = acdc_converter

    def update(self, time: float, state: SystemState):
        """
        Function to update states regarding the power electronics unit

        Parameters
        ----------
        state :
            current SystemState

        Returns
        -------

        """
        ac_power = self.__check_power_limits(state)
        dc_power = self.get_dc_power_from(ac_power, state.dc_circuit_voltage)
        state.pe_losses = abs(ac_power - dc_power)
        state.dc_power_intermediate_circuit = dc_power

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    @property
    def volume(self) -> float:
        """
        Volume of power electronics in m3

        Returns
        -------

        """
        volume: float = 0.0
        volume += self.__acdc_converter.volume
        return volume

    def get_dc_power_from(self, ac_power: float, voltage: float) -> float:
        """
        function to get the dc power from the power electronics unit

        Parameters
        ----------
        ac_power :
            requested ac power from the EMS
        voltage :
            DC voltage

        Returns
        -------
        float
            dc power
        """

        if self.__is_charge(ac_power):
            dc_power = self.__charge(ac_power, voltage)
        else:
            dc_power = self.__discharge(ac_power, voltage)
        return dc_power

    def update_ac_power_from(self, state: SystemState) -> None:
        """
        function to update ac power if fulfillment is not 100 %

        Parameters
        ----------
        state :
            current SystemState

        Returns
        -------

        """
        dc_power_delivered = state.dc_power_intermediate_circuit - state.dc_power_additional
        if self.__is_charge(dc_power_delivered):
            ac_power_converter = self.__acdc_converter.to_dc_reverse(dc_power_delivered, state.dc_circuit_voltage)
        else:
            ac_power_converter = self.__acdc_converter.to_ac_reverse(dc_power_delivered, state.dc_circuit_voltage)
        if abs(ac_power_converter) > self.max_power * 1.1:  # acceptable overload of 10%
            self.__log.error('Power electronics is not able to deliver full power requested of ' +
                             str(int(ac_power_converter)) + ' W (max. power: ' + str(int(self.max_power)) + ' W)')
        state.ac_power_delivered = ac_power_converter + state.aux_losses
        state.pe_losses = abs(ac_power_converter - dc_power_delivered)
        state.dc_power_intermediate_circuit = dc_power_delivered

    @staticmethod
    def __is_charge(power: float) -> bool:
        """
        Function to check, if the system is charged or discharged

        Parameters
        ----------
        power :
            ac power

        Returns
        -------
        bool
            true if the system is charged

        """
        return True if power > 0 else False

    def __charge(self, ac_power: float, voltage: float) -> float:
        """
        function to get the dc power from the power electronics unit if the system is charged

        Parameters
        ----------
        ac_power :
            requested ac power from the EMS
        voltage :
            DC voltage

        Returns
        -------
        float
            dc power
        """
        power_dc = self.__acdc_converter.to_dc(ac_power, voltage)
        return power_dc

    def __discharge(self, ac_power: float, voltage: float) -> float:
        """
        function to get the dc power from the power electronics unit if the system is discharged

        Parameters
        ----------
        ac_power :
            requested ac power from the EMS
        voltage :
            DC voltage

        Returns
        -------
        float
            dc power
        """

        power_dc = self.__acdc_converter.to_ac(ac_power, voltage)
        return power_dc

    def __check_power_limits(self, state: SystemState) -> float:
        """
        Checks if the requested ac power can be handled by the PE unit

        Parameters
        ----------
        state :
            current SystemState

        Returns
        -------
        float
            ac_power, which can be handled by the PE unit

        """
        # TODO Is this the right place for integrating aux losses?
        # Please see Issue 113 (https://gitlab.lrz.de/ees-ses/simses/-/issues/113)
        ac_power = state.ac_power
        if abs(ac_power) > self.__acdc_converter.standby_power_threshold:
            ac_power -= state.aux_losses
        if abs(ac_power) > self.__acdc_converter.max_power:
            self.__log.warn('Requested power (' + str(ac_power) + ') is beyond the maximum power of the '
                            'power electronics. Power is set to: '+ str(self.__acdc_converter.max_power))
            state.fulfillment = self.__acdc_converter.max_power / abs(ac_power)
            return np.sign(ac_power) * self.__acdc_converter.max_power
        else:
            state.fulfillment = 1.0
            return ac_power

    @property
    def max_power(self) -> float:
        return self.__acdc_converter.max_power

    @property
    def acdc_converter_type(self) -> str:
        """
        Returns the name of the selected acdc converter

        Parameters
        ----------

        Returns
        -------
        str
            name of the selected acdc converter

        """
        return type(self.__acdc_converter).__name__

    def close(self) -> None:
        """
        Closing all open resources in the power electronics unit

        Parameters
        ----------

        Returns
        -------

        """
        self.__acdc_converter.close()
        self.__log.close()
