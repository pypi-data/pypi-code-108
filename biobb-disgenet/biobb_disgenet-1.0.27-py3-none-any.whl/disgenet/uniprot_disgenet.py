#!/usr/bin/env python3

"""Module containing the BioBBs DisGeNET class and the command line interface."""
import argparse
import shutil
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_disgenet.disgenet.common import *


# 1. Rename class as required
class Uniprot_disgenet(BiobbObject):
    """
    | biobb_disgenet Gene Uniprot Association Disgenet
    | This class is for downloading a Gene associations file from DisGeNET database using the Uniprot ID of the input.
    | Wrapper for the DisGeNET database `https://www.disgenet.org` and the  DisGeNET REST API ´https://www.disgenet.org/api/´ for downloading available collections of genes and variants associated data to human diseases.

    Args:
        association_type (str): The Uniprot ID is only contempleated for the Gene Disease and Gene attribute associations, so it is necessary to choose between the two. 
        uniprot_id (str): Uniprot code of the input that any associations informations are needed. 
        output_file_path (str): Path to the output file, that can be in format TSV, JSON or XML. 
        properties (dict - Python dict containing the properties for the API interrogation, considering also the credentials of the user to the database):
            * **disease** (*str*) - Disease id or a list of disease separated by commas.
            * **type** (*str*) - Disease, phenotype, group.
            * **source** (*str*) - Source of the associations (CURATED, INFERRED, ANIMAL_MODELS, ALL, BEFREE, CGI, CLINGEN, CLINVAR, CTD_human, CTD_mouse, CTD_rat, GENOMICS_ENGLAND, GWASCAT, GWASDB, HPO, LHGDN, MGD, ORPHANET, PSYGENET, RGD, UNIPROT).
            * **vocabulary** (*str*) - Disease vocabulary (icd9cm, icd10, mesh, omim, do, efo, nci, hpo, mondo, ordo).
            * **disease_class** * - MeSh disease classes.
            * **min_score** (*str*) -  Min value of the gene-disease score range.
            * **max_score** (*str*) -  Max value of the gene-disease score range.
            * **min_ei** (*str*) -  Min value of evidence index score range.
            * **max_ei** (*str*) -  Max value of evidence index score range.
            * **max_dsi** (*str*) - Max value of DSI range for the gene.
            * **min_dsi** (*str*)  - Min value of DSI range for the gene.
            * **max_pli** (*str*) -  Max value of pLI range for the gene.
            * **min_pli** (*str*) -  Min value of pLI range for the gene.
            * **format** (*str*) - Format output file.
            * **limit** (*str*) - Number of GDAs to retrieve.
            * **min_yea** (*str*) - The year of the earliest publications.
            * **max_year** (*str*) - The year of the latest publicatons.
            * **offset** (*str*) - Starting offset of the page.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python:

            from biobb_disgenet.disgenet.gda_disgenet import gda_disgenet

            prop = { 
                'disease': 'disease_id',
                'source': 'source', 
                'min_score': 'min_score',
                'max_score': 'max_score',
                'min_ei': 'min_ei',
                'max_ei': 'max_ei',
                'type': 'disease_type',
                'disease_class': 'disease_class',
                'min_dsi': 'min_dsi',
                'max_dsi': 'max_dsi',
                'min_dpi': 'min_dpi',
                'max_dpi': 'max_dpi',
                'min_pli': 'min_pli',
                'max_pli':'max_pli', 
                'format': 'format',
                'limit': 'limit'
            }
            uniprot_disgenet(association_type='gene-disease',
                    uniprot_id='P02794',
                    output_file_path='output_gene_351',
                    properties=prop)

    Info:

    """

    # 2. Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, association_type, uniprot_id, output_file_path, 
                properties = None, **kwargs) -> None:
        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)

        # 2.1 Modify to match constructor parameters
        # Input/Output files
        self.io_dict = { 
                'in': {'association_type': association_type, 'uniprot_id': uniprot_id}, 
            'out': { 'output_file_path': output_file_path } 
        }

        # 3. Include all relevant properties here as 
        # self.property_name = properties.get('property_name', property_default_value)

        # Properties specific for BB
        self.disease = properties.get('disease', None)
        self.source = properties.get('source', "ALL")
        self.min_score = properties.get('min_score', None)
        self.max_score = properties.get('max_score', None)
        self.min_ei = properties.get('min_ei', None)
        self.max_ei = properties.get('max_ei', None)
        self.type = properties.get('disease_type', None)
        self.disease_class = properties.get('disease_class', None)
        self.min_dsi = properties.get('min_dsi', None)
        self.max_dsi = properties.get('max_dsi', None)
        self.max_dpi = properties.get('max_dpi', None)
        self.min_dpi = properties.get('min_dpi', None)
        self.max_pli = properties.get('max_pli', None)
        self.min_pli = properties.get('min_pli', None)
        self.format = properties.get('format', "json")
        self.limit = properties.get('limit', None)
        self.properties = properties

        # Check the properties

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`GDA_disgenet <disgenet.GDA_disgenet.GDA_disgenet>` object."""
        
        # 4. Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()
        
        #check if the output path exists and mandatory params are there
        output_path = check_output_path(self.io_dict["out"]["output_file_path"], False, "output", self.properties["format"], self.out_log, self.__class__.__name__)
        #check_mandatory_property_properties(self.properties, self.io_dict["in"]["retrieve_by"], 'retrieve_by', self.out_log, self.__class__.__name__)

        #Atuhorized the session based on the session request
        #response = create_session_request("gda", self.io_dict["in"]["retrieve_by"], self.properties, self.out_log, self.global_log)
        response = create_uniprot_request(self.io_dict["in"]["association_type"], self.io_dict["in"]["uniprot_id"], self.properties, self.out_log, self.global_log) 
        auth_session(response, self.properties, output_path, self.out_log, self.global_log)
        #auth_session("gda", self.io_dict["in"]["retrieve_by"], self.properties, output_path, self.out_log, self.global_log
        
        return self.return_code

def uniprot_disgenet(association_type: str, uniprot_id: str,  output_file_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Template <template.template.Template>` class and
    execute the :meth:`launch() <template.template.Template.launch>` method."""

    return Uniprot_disgenet(
                    association_type=association_type,
                    uniprot_id=uniprot_id, 
                    output_file_path=output_file_path,
                    properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='This class is a wrapper for an associations call of teh DisGeNET database REST API.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # 10. Include specific args of each building block following the examples. They should match step 2
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--association_type', required=True, help='Research type necessary to define the the associations: gene-disease, gene-attributes')
    required_args.add_argument('--uniprot_id', required=True, help='Uniprot code to identify the input gene to search for')
    required_args.add_argument('--output_file_path', required=True, help='Description for the output file path. Accepted formats: json, csv or html.')
    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # 11. Adapt to match Class constructor (step 2)
    # Specific call of each building block
    uniprot_disgenet(
             association_type=association_type,
             uniprot_id=uniprot_id,
             output_file_path=output_file_path,
             properties=properties)

if __name__ == '__main__':
    main()

# 12. Complete documentation string


