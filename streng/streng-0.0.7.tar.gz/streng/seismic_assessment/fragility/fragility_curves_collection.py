from dataclasses import dataclass
from typing import List
from cached_property import cached_property
from lxml import etree
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

from . import FragilityCurves, FragilityCurvesLognormal


@dataclass
class FragilityCurvesCollection:
    FragilityCurvesList: List[FragilityCurves]

    def get_oq_fragility_xml(self, description: str, save_file: str = '') -> str:
        limit_states = self.FragilityCurvesList[0].damage_state_descriptions

        root = etree.Element("fragilityModel")
        etree.SubElement(root, "description").text = description
        etree.SubElement(root, "limitStates").text = ' '.join(limit_states)

        for fc in self.FragilityCurvesList:
            fc.get_oq_xml_element_fragility(root)

        xml_string = etree.tostring(root, pretty_print=True).decode("utf-8")

        if save_file != '':
            with open(save_file, "w", encoding='utf-8') as f:
                f.write(xml_string)

        return xml_string

    def get_oq_vulnerability_xml(self, description: str, save_file: str = '') -> str:
        root = etree.Element("vulnerabilityModel")
        root.set('id', 'vulnerability_curves')
        root.set('assetCategory', 'buildings')
        root.set('lossCategory', 'structural')
        etree.SubElement(root, "description").text = description

        for fc in self.FragilityCurvesList:
            fc.get_oq_xml_element_vulnerability(root)

        xml_string = etree.tostring(root, pretty_print=True).decode("utf-8")

        if save_file != '':
            with open(save_file, "w", encoding='utf-8') as f:
                f.write(xml_string)

        return xml_string

    @classmethod
    def from_open_quake_xml(cls, filename):
        fragility_curves = []

        tree = ET.parse(filename)
        root = tree.getroot()

        damage_state_names = root.findtext('./limitStates').split()

        for elem in root.findall('fragilityFunction'):

            _id = elem.get('id')
            _format = elem.get('format')
            _units = 'g'
            _poes = []

            for child in elem:
                # print(child.tag, child.attrib)

                if child.tag == 'imls':
                    _intensity_measure = child.attrib['imt']
                    _intensity_measure_values = child.text.split()
                else:
                    _poes.append(child.text.split())

                # print(_poes)
                # print(_intensity_measure_values)
            fc = FragilityCurves(typology=_id,
                                 format=_format,
                                 intensity_measure=_intensity_measure,
                                 units=_units,
                                 dataframe=pd.DataFrame(index=np.array(_intensity_measure_values, np.float64),
                                                        data=np.array(_poes, np.float64).transpose(),
                                                        columns=damage_state_names).rename_axis(_intensity_measure,
                                                                                                axis=0))

            fragility_curves.append(fc)

        collection = cls(FragilityCurvesList=fragility_curves)

        return collection

    @cached_property
    def to_dict(self):
        d = {}
        for fc in self.FragilityCurvesList:
            d[fc.typology] = fc

        return d
