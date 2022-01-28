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
class Ass_disgenet(BiobbObject):
    """
    | biobb_disgenet Association Disgenet
    | This class is for downloading a Disease Associations file from DisGeNET database.
    | Wrapper for the DisGeNET database `https://www.disgenet.org` and the  DisGeNET REST API ´https://www.disgenet.org/api/´ for downloading available collections of genes and variants associated data to human diseases.

    Args:
        association_type (str): Defition of what type of association is wanted from the DisGeNET REST API from the user (Gene-Disease, Variant-Disease)
        retrieve_by (str): Configiration params to pass for the retrieval of the association on the REST API (gene, uniprot_entry, disease, source, evidences_gene, evidences_disease)
        input_email (str): E-mail used by the user to register to the database (Password would be requested after)
        output_file_path (str): Path to the output file, that can be in format TSV, JSON or XML. 
        properties (dict - Python dict containing the properties for the API interrogation, considering also the credentials of the user to the database):
            * **gene_id** (*str*) - Number identification for a gene or a list of genes separated by commas recognized by the database.
            * **uniprot_id** (*str*) - Uniprot identification number for a gene recognized by the database.
            * **disease** (*str*) - Disease id or a list of disease separated by commas.
            * **disease_type** (*str*) - Disease, phenotype, group.
            * **source** (*str*) - Source of the associations (CURATED, INFERRED, ANIMAL_MODELS, ALL, BEFREE, CGI, CLINGEN, CLINVAR, CTD_human, CTD_mouse, CTD_rat, GENOMICS_ENGLAND, GWASCAT, GWASDB, HPO, LHGDN, MGD, ORPHANET, PSYGENET, RGD, UNIPROT).
            * **disease_vocabulary** (*str*) - Disease vocabulary (icd9cm, icd10, mesh, omim, do, efo, nci, hpo, mondo, ordo).
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
            * **offset** (*str*) - Satrrting offset of the page.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python:

            from biobb_disgenet.disgenet.ass_disgenet import ass_disgenet

            prop = { 
                'gene': 'gene_id',
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
            ass_disgenet(association_type='Gene-Disease',retrieve_by='gene',
                    output_file_path='/path/to/associationsFile',
                    properties=prop)

    Info:

    """

    # 2. Adapt input and output file paths as required. Include all files, even optional ones
    def __init__(self, association_type, retrieve_by, output_file_path, 
                properties = None, **kwargs) -> None:
        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)

        # 2.1 Modify to match constructor parameters
        # Input/Output files
        self.io_dict = { 
                'in': { 'association_type': association_type, 'retrieve_by': retrieve_by }, 
            'out': { 'output_file_path': output_file_path } 
        }

        # 3. Include all relevant properties here as 
        # self.property_name = properties.get('property_name', property_default_value)

        # Properties specific for BB
        self.gene = properties.get('gene', None)
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
        
        #check mandatory params that is gene_id
        check_mandatory_property_properties(self.properties, self.io_dict["in"]["retrieve_by"], 'retrieve_by', self.out_log, self.__class__.__name__)

        #Try1 function
        response = auth(self.io_dict["in"]["association_type"], self.io_dict["in"]["retrieve_by"], self.properties, self.out_log, self.global_log)
        #function to wirte the file then (for now print it)

        # Creating temporary folder
#        self.tmp_folder = fu.create_unique_dir()
#        fu.log('Creating %s temporary folder' % self.tmp_folder, self.out_log)

        # 5. Include here all mandatory input files
        # Copy input_file_path1 to temporary folder
#        shutil.copy(self.io_dict['in']['input_file_path1'], self.tmp_folder)

        # 6. Prepare the command line parameters as instructions list
#        instructions = ['-j']
#        if self.boolean_property:
#            instructions.append('-v')
#            fu.log('Appending optional boolean property', self.out_log, self.global_log)

        # 7. Build the actual command line as a list of items (elements order will be maintained)
#        self.cmd = [self.executable_binary_property,
#               ' '.join(instructions), 
#               self.io_dict['out']['output_file_path'],
#               str(PurePath(self.tmp_folder).joinpath(PurePath(self.io_dict['in']['input_file_path1']).name))]
#        fu.log('Creating command line with instructions and required arguments', self.out_log, self.global_log)

        # 8. Repeat for optional input files if provided
#        if self.io_dict['in']['input_file_path2']:
#            # Copy input_file_path2 to temporary folder
#            shutil.copy(self.io_dict['in']['input_file_path2'], self.tmp_folder)
#            # Append optional input_file_path2 to cmd
#            self.cmd.append(str(PurePath(self.tmp_folder).joinpath(PurePath(self.io_dict['in']['input_file_path2']).name)))
#            fu.log('Appending optional argument to command line', self.out_log, self.global_log)

        # 9. Uncomment to check the command line 
        # print(' '.join(cmd))

        # Run Biobb block
#        self.run_biobb()

        # Remove temporary file(s)
#        if self.remove_tmp: 
#            self.tmp_files.append(self.tmp_folder)
#            self.remove_tmp_files()

        return self.return_code

def ass_disgenet(association_type: str, retrieve_by: str , output_file_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Template <template.template.Template>` class and
    execute the :meth:`launch() <template.template.Template.launch>` method."""

    return Ass_disgenet(association_type=association_type,
                    retrieve_by=retrieve_by,
                    output_file_path=output_file_path,
                    properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='This class is a wrapper for an associations call of teh DisGeNET database REST API.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # 10. Include specific args of each building block following the examples. They should match step 2
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--association_type', required=True, help='Choosing which type of association to call, Gene or Variant ones availables.')
    parser.add_argument('--retrieve_by', required=False, help='Retrieval factor necessary to define the search of the associations; gene, uniprot entry, disease, source, evidence by disease, evidence by gene available choices.')
    required_args.add_argument('--output_file_path', required=True, help='Description for the output file path. Accepted formats: json, csv or html.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # 11. Adapt to match Class constructor (step 2)
    # Specific call of each building block
    ass_disgenet(association_type=association_type, 
             retrieve_by=retrieve_by, 
             output_file_path=output_file_path,
             properties=properties)

if __name__ == '__main__':
    main()

# 12. Complete documentation strings
