from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import numpy


class XmlReader:

    def __init__(self, filename: str):
        tree: ElementTree = ElementTree.parse(filename)
        self.__root: Element = tree.getroot()

    def show_all(self) -> None:
        self.show(self.__root)
        print('total amount of root items:', len(self.__root))
        self.show_subelement_names_of(self.__root)
        print('---')
        for elem in self.__root:
            elem: Element = elem
            self.show_all_subelements_of(elem)

    def show_subelement_names_of(self, element: Element) -> None:
        elements: [str] = self.get_subelement_names_of(element)
        print(elements)

    def get_subelement_names_of(self, element: Element) -> [str]:
        elements: [str] = list()
        for elem in element:
            elements.append(elem.tag)
        return elements

    def show_all_subelements_of(self, element: Element) -> None:
        if element:
            print('')
            self.show(element)
            for subelement in element:
                self.show_all_subelements_of(subelement)
        else:
            self.show(element)

    def show(self, element: Element):
        tag: str = element.tag
        attr: dict = element.attrib
        text: str = element.text
        print('tag:', tag, ', attr:', attr, ', text:', text)

    def get_element(self, name: str, element: Element = None) -> Element:
        if element is None:
            element = self.__root
        return element.find(name)

    def get_value_from(self, element: Element) -> str:
        if element:
            raise ValueError('XML element has children: ' + str(self.get_subelement_names_of(element)))
        return element.text

    def __parse_to_array(self, value: str, delimiter: str) -> numpy.ndarray:
        values: [float] = list()
        for val in value.split(delimiter):
            values.append(float(val))
        return numpy.array(values)

    def __parse_to_matrix(self, value: str, row_delimiter: str, column_delimiter: str) -> numpy.ndarray:
        matrix: [[float]] = list()
        for row in value.split(row_delimiter):
            values: [float] = list()
            for val in row.split(column_delimiter):
                values.append(float(val))
            matrix.append(values)
        return numpy.array(matrix)

    def parse(self, element: Element, row_delimiter: str = ';', column_delimiter: str = ',') -> numpy.ndarray:
        value: str = self.get_value_from(element)
        if row_delimiter in value:
            return self.__parse_to_matrix(value, row_delimiter, column_delimiter)
        else:
            return self.__parse_to_array(value, column_delimiter)

    # # find the first 'item' object
    # for elem in root:
    #     print(elem.find('item').get('name'))
    #
    # # find all "item" objects and print their "name" attribute
    # for elem in root:
    #     for subelem in elem.findall('item'):
    #         subelem: SubElement = subelem
    #         # if we don't need to know the name of the attribute(s), get the dict
    #         print(subelem.attrib)
    #
    #         # if we know the name of the attribute, access it directly
    #         print(subelem.get('name'))


if __name__ == '__main__':
    path: str = '../../data/lithium_ion/isea/i3Cell.xml'
    xml: XmlReader = XmlReader(path)
    custom_definitions: Element = xml.get_element('CustomDefinitions')
    xml.show_subelement_names_of(custom_definitions)
    print('---')
    ocv: Element = xml.get_element('MyOCV', custom_definitions)
    ocv_object: Element = xml.get_element('Object', ocv)
    ocv_data: Element = xml.get_element('LookupData', ocv_object)
    soc: Element = xml.get_element('MeasurementPointsRow', ocv_object)
    temperature: Element = xml.get_element('MeasurementPointsColumn', ocv_object)
    ocv_values: numpy.ndarray = xml.parse(ocv_data)
    soc_values: numpy.ndarray = xml.parse(soc)
    print(type(ocv_values), ocv_values)
    print(type(soc_values), soc_values)
    # xml.show_subelement_names_of(ocv_object)
