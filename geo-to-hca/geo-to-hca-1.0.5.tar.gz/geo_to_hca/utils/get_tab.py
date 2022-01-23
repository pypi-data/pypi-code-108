# --- core imports
from functools import partial
import logging

# --- third-party imports
import pandas as pd

# ---application imports
from geo_to_hca.utils import utils

log = logging.getLogger(__name__)


def get_sequence_file_tab_xls(srp_metadata_update: pd.DataFrame,workbook: object,tab_name: str) -> pd.DataFrame:
    """
    Fills Sequence file metadata fields where the required fields are available in the input dataframe. Writes this tab.
    """
    tab = utils.get_empty_df(workbook,tab_name)
    for index,row in srp_metadata_update.iterrows():
        tab = tab.append({'sequence_file.file_core.file_name': row['fastq_name'],
                          'sequence_file.file_core.format': 'fastq.gz',
                          'sequence_file.file_core.content_description.text':'DNA sequence',
                          'sequence_file.read_index': row['file_index'],
                          'sequence_file.lane_index': row['lane_index'],
                          'sequence_file.insdc_run_accessions': row['Run'],
                          'process.insdc_experiment.insdc_experiment_accession': row['Experiment'],
                          'cell_suspension.biomaterial_core.biomaterial_id':row['Experiment'],
                          'library_preparation_protocol.protocol_core.protocol_id':'',
                          'sequencing_protocol.protocol_core.protocol_id':'',
                          'process.process_core.process_id':row['Run']}, ignore_index=True)
    tab = tab.sort_values(by='sequence_file.insdc_run_accessions')
    return tab


def get_cell_suspension_tab_xls(srp_metadata_update: pd.DataFrame,workbook: object,tab_name: str) -> None:
    """
    Fills Cell suspension metadata fields where the required fields are available in the input dataframe. Writes this tab.
    """
    tab = utils.get_empty_df(workbook, tab_name)
    experiments_dedup = list(set(list(srp_metadata_update['Experiment'])))
    for experiment in experiments_dedup:
        biosample = list(srp_metadata_update.loc[srp_metadata_update['Experiment'] == experiment]['BioSample'])[0]
        gsm_sample = list(srp_metadata_update.loc[srp_metadata_update['Experiment'] == experiment]['SampleName'])[0]
        tab = tab.append({'cell_suspension.biomaterial_core.biomaterial_id':experiment,
                          'cell_suspension.biomaterial_core.biomaterial_name':gsm_sample,
                         'specimen_from_organism.biomaterial_core.biomaterial_id':biosample,
                          'cell_suspension.biomaterial_core.ncbi_taxon_id':list(srp_metadata_update.loc[srp_metadata_update['Experiment'] == experiment]['TaxID'])[0],
                         'cell_suspension.genus_species.text':list(srp_metadata_update.loc[srp_metadata_update['Experiment'] == experiment]['ScientificName'])[0],
                         'cell_suspension.biomaterial_core.biosamples_accession':biosample}, ignore_index=True)
    tab = tab.sort_values(by='cell_suspension.biomaterial_core.biomaterial_id')
    utils.write_to_wb(workbook, tab_name, tab)

def process_specimen_from_organism(biosample_attribute_list: [],srp_metadata_update: pd.DataFrame) -> pd.DataFrame:
    """
    Fills Specimen from organism metadata fields where the required fields are available in the input biosample attribute list.
    """
    df = {'specimen_from_organism.biomaterial_core.biomaterial_id':biosample_attribute_list[0],
          'specimen_from_organism.biomaterial_core.biomaterial_name':biosample_attribute_list[1],
          'specimen_from_organism.biomaterial_core.biomaterial_description': ','.join(biosample_attribute_list[2]),
          'specimen_from_organism.biomaterial_core.ncbi_taxon_id': list(srp_metadata_update.loc[srp_metadata_update['BioSample'] == biosample_attribute_list[0]]['TaxID'])[0],
          'specimen_from_organism.genus_species.text': list(srp_metadata_update.loc[srp_metadata_update['BioSample'] == biosample_attribute_list[0]]['ScientificName'])[0],
          'specimen_from_organism.genus_species.ontology_label': list(srp_metadata_update.loc[srp_metadata_update['BioSample'] == biosample_attribute_list[0]]['ScientificName'])[0],
          'specimen_from_organism.biomaterial_core.biosamples_accession': biosample_attribute_list[0],
          'specimen_from_organism.biomaterial_core.insdc_sample_accession': list(srp_metadata_update.loc[srp_metadata_update['BioSample'] == biosample_attribute_list[0]]['Sample'])[0],
          'collection_protocol.protocol_core.protocol_id':'',
          'process.insdc_experiment.insdc_experiment_accession':srp_metadata_update[srp_metadata_update['BioSample'] == biosample_attribute_list[0]]['Experiment'].values.tolist()[0]}
    return df


def get_specimen_from_organism_tab_xls(srp_metadata_update: pd.DataFrame,workbook: object,nthreads: int,tab_name: str) -> None:
    """
    Fills Specimen from organism metadata fields based on sample metadata obtained via a request to NCBI SRA
    database with biosample accessions. If specified number of threads nthreads > 1, this function will be
    run in parallel with nthreads. Writes this tab.
    """
    tab = utils.get_empty_df(workbook, tab_name)
    biosample_accessions = list(set(list(srp_metadata_update['BioSample'])))
    attribute_lists = utils.fetch_experimental_metadata(biosample_accessions,accession_type='biosample')
    results = None
    if attribute_lists:
        try:
            with utils.poolcontext(processes=nthreads) as pool:
                results = pool.map(partial(process_specimen_from_organism, srp_metadata_update=srp_metadata_update), attribute_lists)
        except KeyboardInterrupt:
            log.info("Process has been interrupted.")
            pool.terminate()
    if results:
        df = pd.DataFrame(results)
        tab = tab.append(df,sort=True)
        tab = tab.sort_values(by='process.insdc_experiment.insdc_experiment_accession')
        utils.write_to_wb(workbook, tab_name, tab)


def get_library_protocol_tab_xls(srp_metadata_update: pd.DataFrame,workbook: object,tab_name: str) -> [{},[]]:
    """
    Fills Library preparation protocol metadata fields based on experiment metadata obtained via a request to NCBI SRA
    database with experiment accessions. Writes this tab.
    """
    tab = utils.get_empty_df(workbook, tab_name)
    experiment_accessions = list(set(list(srp_metadata_update['Experiment'])))
    count = 0
    library_protocol_set = list()
    library_protocol_dict = {}
    attribute_lists = utils.fetch_experimental_metadata(experiment_accessions,accession_type='experiment')
    for attribute_list in attribute_lists:
        experiment_accession = str(attribute_list[0])
        library_protocol = attribute_list[1]
        if library_protocol not in library_protocol_set:
            count += 1
            library_protocol_id = "library_protocol_" + str(count)
            library_protocol_set.append(library_protocol)
            tmp_dict = {'library_preparation_protocol.protocol_core.protocol_id':library_protocol_id,
                              'library_preparation_protocol.protocol_core.protocol_description': library_protocol,
                              'library_preparation_protocol.input_nucleic_acid_molecule.text': 'polyA RNA',
                              'library_preparation_protocol.nucleic_acid_source':'single cell'}
            library_protocol_dict[experiment_accession] = {"library_protocol_id":library_protocol_id,"library_protocol_description":library_protocol}
            if "10X" in library_protocol:
                if "v.2" or "v2" or 'V2' or 'V.2' in library_protocol:
                    if "3'" in library_protocol:
                        tmp_dict.update({'library_preparation_protocol.cell_barcode.barcode_read': 'Read1',
                                        'library_preparation_protocol.cell_barcode.barcode_offset': 0,
                                        'library_preparation_protocol.cell_barcode.barcode_length': 16,
                                        'library_preparation_protocol.library_construction_method.text':"10X 3' v2 sequencing",
                                        'library_preparation_protocol.library_construction_kit.retail_name': 'Single Cell 3’ Reagent Kit v2',
                                        'library_preparation_protocol.library_construction_kit.manufacturer': '10X Genomics',
                                        'library_preparation_protocol.end_bias':'3 prime tag',
                                        'library_preparation_protocol.primer':'poly-dT',
                                        'library_preparation_protocol.strand':'first',
                                        'library_preparation_protocol.umi_barcode.barcode_read':'Read1',
                                        'library_preparation_protocol.umi_barcode.barcode_offset':16,
                                        'library_preparation_protocol.umi_barcode.barcode_length':10})
                    elif "5'" in library_protocol:
                        log.info("Please let Ami know that you have come across a 10X v2 5' dataset")
                        tmp_dict.update({'library_preparation_protocol.cell_barcode.barcode_read': 'Read1',
                                        'library_preparation_protocol.cell_barcode.barcode_offset': 0,
                                        'library_preparation_protocol.cell_barcode.barcode_length': 16,
                                        'library_preparation_protocol.library_construction_method.text':"10X 5' v2 sequencing",
                                        'library_preparation_protocol.library_construction_kit.retail_name': 'Single Cell 5’ Reagent Kit v2',
                                        'library_preparation_protocol.library_construction_kit.manufacturer': '10X Genomics',
                                        'library_preparation_protocol.end_bias':'5 prime tag',
                                        'library_preparation_protocol.primer':'poly-dT',
                                        'library_preparation_protocol.strand':'first',
                                        'library_preparation_protocol.umi_barcode.barcode_read':'Read1',
                                        'library_preparation_protocol.umi_barcode.barcode_offset':16,
                                        'library_preparation_protocol.umi_barcode.barcode_length':10})
                elif "v.3" or "v3" or 'V3' or 'V.3' in library_protocol:
                    tmp_dict.update({'library_preparation_protocol.cell_barcode.barcode_read': 'Read1',
                                    'library_preparation_protocol.cell_barcode.barcode_offset': 0,
                                    'library_preparation_protocol.cell_barcode.barcode_length': 16,
                                    'library_preparation_protocol.library_construction_method.text':"10X 3' v3 sequencing",
                                    'library_preparation_protocol.library_construction_kit.retail_name': 'Single Cell 3’ Reagent Kit v3',
                                    'library_preparation_protocol.library_construction_kit.manufacturer': '10X Genomics',
                                    'library_preparation_protocol.end_bias':'3 prime tag',
                                    'library_preparation_protocol.primer':'poly-dT',
                                    'library_preparation_protocol.strand':'first',
                                    'library_preparation_protocol.umi_barcode.barcode_read':'"Read1',
                                    'library_preparation_protocol.umi_barcode.barcode_offset':16,
                                    'library_preparation_protocol.umi_barcode.barcode_length':12})
                elif "v.1" or "v1" or 'V1' or 'V.1' in library_protocol:
                    tmp_dict.update({'library_preparation_protocol.cell_barcode.barcode_read': 'Read1',
                                    'library_preparation_protocol.cell_barcode.barcode_offset': 0,
                                    'library_preparation_protocol.cell_barcode.barcode_length': 14,
                                    'library_preparation_protocol.library_construction_method.text':"10X v1 sequencing",
                                    'library_preparation_protocol.library_construction_kit.retail_name': 'Single Cell Reagent Kit v1',
                                    'library_preparation_protocol.library_construction_kit.manufacturer': '10X Genomics',
                                    'library_preparation_protocol.end_bias':'',
                                    'library_preparation_protocol.primer':'poly-dT',
                                    'library_preparation_protocol.strand':'first',
                                    'library_preparation_protocol.umi_barcode.barcode_read':'Read1',
                                    'library_preparation_protocol.umi_barcode.barcode_offset':14,
                                    'library_preparation_protocol.umi_barcode.barcode_length':10})
                else:
                    tmp_dict.update({'library_preparation_protocol.library_construction_method.text': "10X sequencing",
                                     'library_preparation_protocol.library_construction_kit.manufacturer': '10X Genomics'})
                tab = tab.append(tmp_dict, ignore_index=True)
            elif 'Drop-seq' or 'drop-seq' or 'DropSeq' or 'Dropseq' in library_protocol:
                tmp_dict.update({'library_preparation_protocol.cell_barcode.barcode_read': 'Read1',
                                 'library_preparation_protocol.cell_barcode.barcode_offset': 0,
                                 'library_preparation_protocol.cell_barcode.barcode_length': 12,
                                 'library_preparation_protocol.library_construction_method.text': "Drop-seq",
                                 'library_preparation_protocol.library_construction_kit.retail_name': '',
                                 'library_preparation_protocol.library_construction_kit.manufacturer': '',
                                 'library_preparation_protocol.end_bias': '',
                                 'library_preparation_protocol.primer': 'poly-dT',
                                 'library_preparation_protocol.strand': 'first',
                                 'library_preparation_protocol.umi_barcode.barcode_read': 'Read1',
                                 'library_preparation_protocol.umi_barcode.barcode_offset': 12,
                                 'library_preparation_protocol.umi_barcode.barcode_length': 8})
                tab = tab.append(tmp_dict, ignore_index=True)
            elif 'Smart-seq' or 'smart-seq' or 'Smartseq' or 'SmartSeq' or 'plate' or 'Plate' in library_protocol:
                tmp_dict.update({'library_preparation_protocol.cell_barcode.barcode_read': '',
                                 'library_preparation_protocol.cell_barcode.barcode_offset': '',
                                 'library_preparation_protocol.cell_barcode.barcode_length': '',
                                 'library_preparation_protocol.library_construction_method.text': 'Smart-seq2',
                                 'library_preparation_protocol.library_construction_kit.retail_name': '',
                                 'library_preparation_protocol.library_construction_kit.manufacturer': '',
                                 'library_preparation_protocol.end_bias': 'full length',
                                 'library_preparation_protocol.primer': 'poly-dT',
                                 'library_preparation_protocol.strand': 'unstranded',
                                 'library_preparation_protocol.umi_barcode.barcode_read': '',
                                 'library_preparation_protocol.umi_barcode.barcode_offset': '',
                                 'library_preparation_protocol.umi_barcode.barcode_length': ''})
                tab = tab.append(tmp_dict, ignore_index=True)
            else:
                tab = tab
        if library_protocol in library_protocol_set:
            tab = tab
            for key in library_protocol_dict.keys():
                if library_protocol_dict[key]["library_protocol_description"] == library_protocol:
                    library_protocol_id = library_protocol_dict[key]["library_protocol_id"]
            if not library_protocol_id:
                library_protocol_id = ''
            else:
                library_protocol_dict[experiment_accession] = {"library_protocol_id":library_protocol_id,"library_protocol_description":
                library_protocol}
    utils.write_to_wb(workbook, tab_name, tab)
    return library_protocol_dict,attribute_lists


def get_sequencing_protocol_tab_xls(workbook: object,attribute_lists: [],tab_name: str) -> {}:
    """
    Fills Sequencing protocol metadata fields based on experiment metadata obtained via a previous request to NCBI SRA
    database with experiment accessions (attribute_lists). Writes this tab.
    """
    tab = utils.get_empty_df(workbook, tab_name)
    count = 0
    sequencing_protocol_id = "sequencing_protocol_1"
    sequencing_protocol_set = list()
    sequencing_protocol_dict = {}
    for attribute_list in attribute_lists:
        experiment = attribute_list[0]
        library_construction_protocol = attribute_list[1]
        instrument = attribute_list[2]
        if "10X" in library_construction_protocol:
            paired_end = 'no'
            method = 'tag based single cell RNA sequencing'
        elif "10X" not in library_construction_protocol:
            paired_end = ''
            method = ''
        sequencing_protocol_description = [instrument,method]
        if sequencing_protocol_description not in sequencing_protocol_set:
            count += 1
            sequencing_protocol_id = "sequencing_protocol_" + str(count)
            sequencing_protocol_set.append(sequencing_protocol_description)
            sequencing_protocol_dict[experiment] = {"sequencing_protocol_id":sequencing_protocol_id,
                                                    "sequencing_protocol_description":sequencing_protocol_description}
            tab = tab.append({'sequencing_protocol.protocol_core.protocol_id': sequencing_protocol_id,
                              'sequencing_protocol.instrument_manufacturer_model.text': instrument,
                              'sequencing_protocol.paired_end': paired_end,
                              'sequencing_protocol.method.text': method}, ignore_index=True)
        if sequencing_protocol_description in sequencing_protocol_set:
            tab = tab
            for key in sequencing_protocol_dict.keys():
                if sequencing_protocol_dict[key]["sequencing_protocol_description"] == sequencing_protocol_description:
                    sequencing_protocol_id = sequencing_protocol_dict[key]["sequencing_protocol_id"]
            if not sequencing_protocol_id:
                sequencing_protocol_id = ''
            else:
                sequencing_protocol_dict[experiment] = {"sequencing_protocol_id":sequencing_protocol_id,
                                                    "sequencing_protocol_description":sequencing_protocol_description}
    utils.write_to_wb(workbook, tab_name, tab)
    return sequencing_protocol_dict


def update_sequence_file_tab_xls(sequence_file_tab: pd.DataFrame,library_protocol_dict: {},sequencing_protocol_dict: {},workbook: object,tab_name: str) -> None:
    """
    Updates and writes the Sequencing file tab based on the unique Library preparation protocols and Sequencing file protocols obtained previously
    (stored in the input dictionaries: library_protocol_dict and  sequencing_protocol_dict). Specifically this function adds which unique
    library protocol id and sequencing protocol id is associated with each Cell suspension and run accession in the Sequence file tab.
    """
    library_protocol_id_list = list()
    sequencing_protocol_id_list = list()
    for index,row in sequence_file_tab.iterrows():
        if row["cell_suspension.biomaterial_core.biomaterial_id"] in library_protocol_dict.keys():
            library_protocol_id_list.append(library_protocol_dict[row["cell_suspension.biomaterial_core.biomaterial_id"]]["library_protocol_id"])
        else:
            library_protocol_id_list.append('')
        if row["cell_suspension.biomaterial_core.biomaterial_id"] in sequencing_protocol_dict.keys():
            sequencing_protocol_id_list.append(sequencing_protocol_dict[row["cell_suspension.biomaterial_core.biomaterial_id"]]["sequencing_protocol_id"])
        else:
            sequencing_protocol_id_list.append('')
    sequence_file_tab['library_preparation_protocol.protocol_core.protocol_id'] = library_protocol_id_list
    sequence_file_tab['sequencing_protocol.protocol_core.protocol_id'] = sequencing_protocol_id_list
    utils.write_to_wb(workbook, tab_name, sequence_file_tab)


def get_project_main_tab_xls(srp_metadata_update: pd.DataFrame,workbook: object,geo_accession: str,tab_name: str) -> []:
    """
    Fills and writes a Project (main) tab with SRA study and Bioproject metadata obtained via a request to the NCBI SRA database
    with a bioporject accession.
    """
    study = list(srp_metadata_update['SRAStudy'])[0]
    project = list(srp_metadata_update['BioProject'])[0]
    try:
        tab = utils.get_empty_df(workbook,tab_name)
        bioproject = list(set(list(srp_metadata_update['BioProject'])))
        if len(bioproject) > 1:
            log.info("more than 1 bioproject, check this")
        else:
            bioproject = bioproject[0]
        project_name,project_title,project_description,project_pubmed_id = utils.get_bioproject_metadata(bioproject)
        tab = tab.append({'project.project_core.project_title':project_title,
                        'project.project_core.project_description':project_description,
                        'project.geo_series_accessions':geo_accession,
                        'project.insdc_study_accessions':study,
                        'project.insdc_project_accessions':project}, ignore_index=True)
        utils.write_to_wb(workbook, tab_name, tab)
    except AttributeError:
        pass
    return project_name, project_title, project_description, project_pubmed_id


def get_project_publication_tab_xls(workbook: object,tab_name: str,project_pubmed_id: str) -> None:
    """
    Fills and writes the Project publication tab with publication metadata obtained via a request to the NCBI SRA database
    with a bioporject accession.
    """
    tab = utils.get_empty_df(workbook,tab_name)
    title,author_list,grant_list,article_doi_id = utils.get_pubmed_metadata(project_pubmed_id,iteration=1)
    name_list = list()
    for author in author_list:
        name = author[0] + ' ' + author[2] + "||"
        name_list.append(name)
    name_list = ''.join(name_list)
    name_list = name_list[:len(name_list)-2]
    tab = tab.append({'project.publications.authors':name_list,
                      'project.publications.title':title,
                      'project.publications.doi':article_doi_id,
                      'project.publications.pmid':project_pubmed_id,
                      'project.publications.url':''}, ignore_index=True)
    utils.write_to_wb(workbook, tab_name, tab)


def get_project_contributors_tab_xls(workbook: object,tab_name: str,project_pubmed_id: str) -> None:
    """
    Function to fetch publication metadata, specifically about the publication contributors from an xml following a request to NCBI.
    """
    tab = utils.get_empty_df(workbook,tab_name)
    title, author_list, grant_list, article_doi_id = utils.get_pubmed_metadata(project_pubmed_id,iteration=2)
    for author in author_list:
        name = author[1] + ',,' + list(author)[0]
        affiliation = author[3]
        tab = tab.append({'project.contributors.name':name,'project.contributors.institution':affiliation}, ignore_index=True)
    utils.write_to_wb(workbook, tab_name, tab)


def get_project_funders_tab_xls(workbook: object,tab_name: str,project_pubmed_id: str) -> None:
    """
    Function to fetch publication metadata, specifically about the project funders, from an xml following a request to NCBI.
    """
    tab = utils.get_empty_df(workbook,tab_name)
    title, author_list, grant_list, article_doi_id = utils.get_pubmed_metadata(project_pubmed_id,iteration=3)
    for grant in grant_list:
        tab = tab.append({'project.funders.grant_id':grant[0],'project.funders.organization':grant[1]}, ignore_index=True)
    utils.write_to_wb(workbook, tab_name, tab)
