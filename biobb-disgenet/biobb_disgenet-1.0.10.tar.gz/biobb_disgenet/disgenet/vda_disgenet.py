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
class VDA_disgenet(BiobbObject):
    """
    | biobb_disgenet Variant Association Disgenet
    | This class is for downloading a Varinat Disease Associations file from DisGeNET database.
    | Wrapper for the DisGeNET database `https://www.disgenet.org` and the  DisGeNET REST API ´https://www.disgenet.org/api/´ for downloading available collections of genes and variants associated data to human diseases.

    Args:
        retrieve_by (str): Configuration params to pass for the retrieval of the association on the REST API (variant, disease, source)
        output_file_path (str): Path to the output file, that can be in format TSV, JSON or XML. 
        properties (dict - Python dict containing the properties for the API interrogation, considering also the credentials of the user to the database):
            * **gene_id** (*str*) - Number identification for a gene or a list of genes separated by commas recognized by the database.
            * **variant_id** (*str) - Variant id for the gene or a list of variant ids separated by commas recognized by the database.
            * **disease_id** (*str*) - Disease id or a list of disease separated by commas.
            * **type** (*str*) - Disease, phenotype, group.
            * **source** (*str*) - Source of the associations (CURATED, INFERRED, ANIMAL_MODELS, ALL, BEFREE, CGI, CLINGEN, CLINVAR, CTD_human, CTD_mouse, CTD_rat, GENOMICS_ENGLAND, GWASCAT, GWASDB, HPO, LHGDN, MGD, ORPHANET, PSYGENET, RGD, UNIPROT).
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
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python:

            from biobb_disgenet.disgenet.vda_disgenet import vda_disgenet

            prop = { 
                'variant_id': 'variant_id',
                'disease_id': 'disease_id',
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
                'min_year':'min_year',
                'max_year':'max_year',
                'offset':'offset'
            }
            vda_disgenet(retrieve_by='variant',
                    output_file_path='/path/to/associationsFile',
                    properties=prop)

    Info:
            retrieve_by can be: 
                variant, gene, disease, source, evidences

    """

    # 2. Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, retrieve_by, output_file_path,  
                properties = None, **kwargs) -> None:
        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)

        # 2.1 Modify to match constructor parameters
        # Input/Output files
        self.io_dict = { 
                'in': {'retrieve_by': retrieve_by}, 
            'out': { 'output_file_path': output_file_path } 
        }

        # 3. Include all relevant properties here as 
        # self.property_name = properties.get('property_name', property_default_value)

        # Properties specific for BB
        self.gene_id = properties.get('gene_id', None)
        self.variant_id = properties.get('variant_id', None)
        self.disease_id = properties.get('disease_id', None)
        self.source = properties.get('source', "ALL")
        self.vocabulary = properties.get('vocabulary', None)
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
        self.min_year = properties.get('min_year', None)
        self.max_year = properties.get('max_year',None)
        self.offset = properties.get('offset', None)
        self.properties = properties

        # Check the properties

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`VDA_disgenet <disgenet.VDA_disgenet.VDA_disgenet>` object."""
        
        # 4. Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()
        
        #check mandatory params that is gene_id
        output_path = check_output_path(self.io_dict["out"]["output_file_path"], False, "output", self.properties["format"], self.out_log, self.__class__.__name__)
        #Try1 function
        if self.io_dict["in"]["retrieve_by"]:
            response = gda_vda_session("vda", self.io_dict["in"]["retrieve_by"], self.properties, self.out_log, self.global_log)
        else:
            raise SystemExit("Fundamental argument is missing, check the input parameter.")
        new_keys, request = extension_request(response, self.io_dict["in"]["retrieve_by"], self.properties)
        auth_session(request, new_keys, output_path, self.out_log, self.global_log)   
        return self.return_code

def vda_disgenet(retrieve_by: str , output_file_path: str, evidences: bool = False, properties: dict = None, **kwargs) -> int:
    """Create :class:`Template <template.template.Template>` class and
    execute the :meth:`launch() <template.template.Template.launch>` method."""

    return VDA_disgenet(
                    retrieve_by=retrieve_by,
                    output_file_path=output_file_path,
                    properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='This class is a wrapper for an associations call of teh DisGeNET database REST API.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')
    # 10. Include specific args of each building block following the examples. They should match step 2
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--retrieve_by', required=True, help='Retrieval factor necessary to define the search of the associations; gene, uniprot entry, disease, source, evidence by disease, evidence by gene available choices.')
    required_args.add_argument('--output_file_path', required=True, help='Description for the output file path. Accepted formats: json, csv or html.')
    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # 11. Adapt to match Class constructor (step 2)
    # Specific call of each building block
    vda_disgenet(
             retrieve_by=retrieve_by, 
             output_file_path=output_file_path,
             properties=properties)

if __name__ == '__main__':
    main()

# 12. Complete documentation strings
