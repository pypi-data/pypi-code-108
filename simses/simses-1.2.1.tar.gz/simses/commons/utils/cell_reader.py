from xml.etree.ElementTree import Element

import numpy

from simses.commons.utils.xml_reader import XmlReader


class IseaCellReader:

    __EQUIVALENT_CIRCUIT_MODEL: str = 'CustomDefinitions'

    __OPEN_CIRCUIT_VOLTAGE: str = 'MyOCV'
    __OPEN_CIRCUIT_VOLTAGE_OBJECT: str = 'Object'
    __OCV_DATA: str = 'LookupData'
    __OCV_SOC_DATA: str = 'MeasurementPointsRow'
    __OCV_TEMPERATURE_DATA: str = 'MeasurementPointsColumn'

    __INTERNAL_RESISTANCE: str = 'MyOhmicResistanceser'
    __INTERNAL_RESISTANCE_OBJECT: str = 'Object'
    __INTERNAL_RESISTANCE_DATA: str = 'LookupData'
    __INTERNAL_RESISTANCE_SOC_DATA: str = 'MeasurementPointsRow'
    __INTERNAL_RESISTANCE_TEMPERATURE_DATA: str = 'MeasurementPointsColumn'

    def __init__(self, path: str):
        self.__data: XmlReader = XmlReader(path)

    def __get_equivalent_circuit_model(self) -> Element:
        return self.__data.get_element(self.__EQUIVALENT_CIRCUIT_MODEL)

    def __get_open_circuit_voltage(self) -> Element:
        ecm: Element = self.__get_equivalent_circuit_model()
        ocv: Element = self.__data.get_element(self.__OPEN_CIRCUIT_VOLTAGE, ecm)
        return self.__data.get_element(self.__OPEN_CIRCUIT_VOLTAGE_OBJECT, ocv)

    def __get_internal_resistance(self) -> Element:
        ecm: Element = self.__get_equivalent_circuit_model()
        rint: Element = self.__data.get_element(self.__INTERNAL_RESISTANCE, ecm)
        return self.__data.get_element(self.__INTERNAL_RESISTANCE_OBJECT, rint)

    def get_open_cicuit_voltage(self) -> numpy.ndarray:
        ocv: Element = self.__get_open_circuit_voltage()
        ocv_data: Element = self.__data.get_element(self.__OCV_DATA, ocv)
        return self.__data.parse(ocv_data)

    def get_open_cicuit_voltage_soc(self) -> numpy.ndarray:
        ocv: Element = self.__get_open_circuit_voltage()
        soc_data: Element = self.__data.get_element(self.__OCV_SOC_DATA, ocv)
        return self.__data.parse(soc_data)

    def get_open_cicuit_voltage_temperature(self) -> numpy.ndarray:
        ocv: Element = self.__get_open_circuit_voltage()
        temperature_data: Element = self.__data.get_element(self.__OCV_TEMPERATURE_DATA, ocv)
        return self.__data.parse(temperature_data)

    def get_internal_resistance(self) -> numpy.ndarray:
        rint: Element = self.__get_internal_resistance()
        ocv_data: Element = self.__data.get_element(self.__INTERNAL_RESISTANCE_DATA, rint)
        return self.__data.parse(ocv_data)

    def get_internal_resistance_soc(self) -> numpy.ndarray:
        rint: Element = self.__get_internal_resistance()
        soc_data: Element = self.__data.get_element(self.__INTERNAL_RESISTANCE_SOC_DATA, rint)
        return self.__data.parse(soc_data)

    def get_internal_resistance_temperature(self) -> numpy.ndarray:
        rint: Element = self.__get_internal_resistance()
        temperature_data: Element = self.__data.get_element(self.__INTERNAL_RESISTANCE_TEMPERATURE_DATA, rint)
        return self.__data.parse(temperature_data)


if __name__ == '__main__':
    path: str = '../../data/lithium_ion/isea/i3Cell.xml'
    cell_data: IseaCellReader = IseaCellReader(path)
    ocv_values: numpy.ndarray = cell_data.get_open_cicuit_voltage()
    soc_values: numpy.ndarray = cell_data.get_open_cicuit_voltage_soc()
    print(type(ocv_values), ocv_values)
    print(type(soc_values), soc_values)
