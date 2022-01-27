"""
Generate an IMPC xml for the manual annotation procedure
"""

from typing import Tuple
from lxml import etree
import yaml
from vpv.lib import addict


def get_annotator_id_and_date(procedure_id) -> Tuple[str, str]:
    """
    Get the unique annotator_id and annotation date parameter ids for a procedure.

    Parameters
    ----------
    procedure_id

    Returns
    -------
    0: annotator_id
    1: date_of_annotation
    """

    map_ = {
        'IMPC_EOL': ('IMPC_EOL_052_001', 'IMPC_EOL_053_001'),
        'IMPC_EML': ('IMPC_EML_057_001', 'IMPC_EML_058_001'),
        'IMPC_EMO': ('IMPC_EMO_178_001', 'IMPC_EMO_179_001'),
        'IMPC_EMA': ('IMPC_EMA_149_001', 'IMPC_EMA_150_001')
    }

    if procedure_id[:8] not in map_:
        raise ValueError(f'The annotator id and date proecure terms have not been added for {procedure_id[:8]}')
    return map_[procedure_id[:8]]


class ExportXML(object):
    """
    TODO: project
    """
    def __init__(self,
                 date_of_annotation: str,
                 annotator_id: str,
                 metadata: str
                 ):
        """

        Parameters
        ----------
        date_of_annotation
            yyy-mm-dd
        annotator_id
            annonymized annotator id
        metadata
            path to procedure_metadata.yaml
        """

        self.metadata = load_metadata(metadata)
        md = self.metadata

        # Create separate file for each modality
        self.root = etree.Element('centreProcedureSet',
                             xmlns="http://www.mousephenotype.org/dcc/exportlibrary/datastructure/core/procedure")

        centre = etree.SubElement(self.root, 'centre', project=md['project'], pipeline=md['pipeline'],
                                  centreID=md['centre_id'])

        # Create an experiment element
        self.experiment = etree.SubElement(centre, 'experiment', dateOfExperiment=md['dateofexperiment'],
                                      experimentID=md['experiment_id'])

        # Append specimen
        specimen = etree.SubElement(self.experiment, 'specimenID')
        specimen.text = md['specimenid']

        self.procedure_element = etree.SubElement(self.experiment, 'procedure', procedureID=md['procedure_id'])

        annotator_param_id, date_of_annotation_param_id = get_annotator_id_and_date(self.metadata['procedure_id'])
        # Add metadata parameters that are not supplied in the procedure_metadata.yaml
        self.metadata['metadata'][annotator_param_id] = annotator_id
        self.metadata['metadata'][date_of_annotation_param_id] = date_of_annotation

    def add_metadata(self):
        for id_, param_value in self.metadata['metadata'].items():
            parameter = etree.SubElement(self.procedure_element, 'procedureMetadata', parameterID=id_)
            # Create value element
            value = etree.SubElement(parameter, 'value')
            value.text = str(param_value)

    def write(self, file_path):
        # print etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone='yes')
        etree.ElementTree(self.root).write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                      standalone='yes')

    def add_series_media_parameter(self, parameter_id: str):
        """
        Add SMP which will have parameterAssociations attached to it later (annotation points)

        Parameters
        ----------
        parameter_id: the IMPC reconstruction parameter

        """
        smp = etree.SubElement(self.procedure_element,
                               'seriesMediaParameter',
                               parameterID=parameter_id)

        smp_value = etree.SubElement(smp, 'value',
                                     {"incrementValue": "1",  "URI": self.metadata['reconstruction_url']})

        # Add the deafault images parameter
        self.series_media_parameter = smp_value

    def add_point(self, param_id, xyz, xyz_percents):
        """
        Annotation points cannot be added to the manual annotation call as it is a simpleParameter
        Instead, we have to create a seriesMediaParameter and add it there with a link to the manual annotation
        parameter

        Parameters
        ----------
        param_id: str
            The parameter ID to link the point to
        param_and_id: tuple
            The annotation parameter
        xyz: tuple (int)
            the location of the annotation mark
        xyz_percents: tuple
            the percentage distances of the annotation mark from the origin

        Notes
        -----
        IMPC_EMO_001_001 is the parameter ID for embryo reconstructions


        The final series media parameter for an annotation point should look like this

            <parameterAssociation  parameterID="IMPC_EMO_022_001“>
            <dim origin="topLeft" id="x">700</dim>
            <dim origin="topLeft" id="y">350</dim>
            <dim origin="topLeft" id="z">500</dim>
            <dim origin="topLeft" id="x_percent">24.6</dim>
            <dim origin="topLeft" id="y_percent">34.7</dim>
            <dim origin="topLeft" id="z_percent">15.4</dim>
        """

        param_assoc = etree.SubElement(self.series_media_parameter,
                                       'parameterAssociation',
                                       {'parameterID': param_id})

        def put_in_points(ids, values):
            for id_, value in zip(ids, values):
                etree.SubElement(param_assoc,
                                 'dim',
                                 {'origin': 'RAS',
                                  'id': id_}).text = str(value)

        put_in_points(['x', 'y', 'z'], xyz)
        put_in_points(['x_percent', 'y_percent', 'z_percent'], xyz_percents)


    def add_parameter(self, param_id, param_value):
        """
        Add a manual annotation parameter to the XML

        Parameters
        ----------
        param_id: str
            The parameter ID for this annotation. Now ewe are using IMPRESS paarameters
            eg: IMPC_EMO_022_001  see https://www.mousephenotype.org/impress/parameterontologies/19112/495

        param_value: str
            Value associated with this annotation.
            for example: "abnormal"
        x,y,z: int or None
            the optional points associated with this annotation (can be None)
        Notes
        -----
        Adapted from James Brown's http://phobos/james.brown/export_xml_generation

        """

        # Get parameter info and append to procedure
        parameter = etree.SubElement(self.procedure_element, 'simpleParameter', parameterID=param_id)

        # Create value element
        value = etree.SubElement(parameter, 'value')
        value.text = param_value
        return parameter


def load_metadata(yaml_path):
    """
    Load in the procedure_metadata yaml file - Update the version ID to be 002 for now
    increase the procedureID if at 001 as this needs to be version 002 for validation

    Parameters
    ----------
    yaml_path: str
        path to config file

    Returns
    -------
    dict

    """

    with open(yaml_path, 'r') as fh:
        data = yaml.load(fh)

    # override the procedure ID
    proc_id: str = data['procedure_id'].replace('_001', '_002')
    data['procedure_id'] = proc_id

    return data


def load_xml(xml_file) -> Tuple:
    """
    Reads in a manual annotation xml file
    """

    try:
        root = etree.parse(xml_file)
    except (etree.XMLSyntaxError, IOError) as e:
        raise IOError(e.msg)

    root = strip_ns_prefix(root)

    simple_params = addict.Dict()
    procedure_metadata = []

    for a in root.iter():
        if a.tag == 'centre':
            centreID = a.attrib['centreID']
            pipeline = a.attrib['pipeline']
            project = a.attrib['project']

        elif a.tag == 'experiment':
            doe = a.attrib['dateOfExperiment']
            ex_id = a.attrib['experimentID']

        elif a.tag == 'specimenID':
            spec_id = a.text

        elif a.tag == 'procedure':
            # proc_id = a.attrib['procedureID']  hard code to v2
            proc_id = a.attrib['procedureID']

        elif a.tag == 'simpleParameter':
            param_id = a.attrib['parameterID']
            value = a.find('value').text
            simple_params[param_id].option = value

        elif a.tag == 'procedureMetadata':
            param_id = a.attrib['parameterID']
            value = a.find('value').text
            procedure_metadata.append((param_id, value))

        elif a.tag == 'seriesMediaParameter':
            for b in a.iter():
                param_assocs = b.findall('parameterAssociation')
                for assoc in param_assocs:
                    param_id = assoc.attrib['parameterID']
                    for dim in assoc.findall('dim'):
                        if dim.attrib['id'] == 'x':
                            x = dim.text
                        elif dim.attrib['id'] == 'y':
                            y = dim.text
                        elif dim.attrib['id'] == 'z':
                            z = dim.text
                    simple_params[param_id].xyz = (x, y, z)

    return centreID, pipeline, project, doe, ex_id, spec_id, proc_id, simple_params, procedure_metadata


def strip_ns_prefix(tree):
    """
    remove the namespace from the tree
    Parameters
    ----------
    tree

    Returns
    -------

    """
    #xpath query for selecting all element nodes in namespace
    query = "descendant-or-self::*[namespace-uri()!='']"
    #for each element returned by the above xpath query...
    for element in tree.xpath(query):
        #replace element name with its local name
        element.tag = etree.QName(element).localname
    return tree
