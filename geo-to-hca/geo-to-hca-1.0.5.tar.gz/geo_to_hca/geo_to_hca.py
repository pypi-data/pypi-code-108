# --- core imports
import argparse
import logging
import os
from pathlib import Path
import sys

# --- third-party imports
import pandas as pd
from openpyxl import load_workbook, Workbook

# --- application imports
from geo_to_hca.utils import get_tab
from geo_to_hca.utils import parse_reads
from geo_to_hca.utils import sra_utils
from geo_to_hca.utils import utils

DEFAULT_HCA_TEMPLATE = Path(__file__).resolve().parents[1] / "template/hca_template.xlsx"
log = logging.getLogger(__name__)


def fetch_srp_accession(geo_accession: str) -> str:
    """
    Function to retrieve an SRA study accession given a GEO accession.
    """
    srp = sra_utils.SraUtils.get_srp_accession_from_geo(geo_accession)
    if not srp.empty:
        if srp.shape[0] == 1:
            srp = srp.iloc[0]["study_accession"]
        elif srp.shape[0] > 1:
            raise Exception("More than 1 accession has been found. Please enter re-try with a single SRA Study "
                            "accession.")
    else:
        raise Exception(f"Could not recognise GEO accession {geo_accession}; is it a GEO Superseries? If yes, please "
                        f"re-try with a "
                        "subseries accession")
    return srp


def fetch_srp_metadata(srp_accession: str) -> pd.DataFrame:
    """
    Function to get various metadata from the SRA database given an SRA study accession.
    """
    srp_metadata_df = sra_utils.SraUtils.get_srp_metadata(srp_accession)
    return srp_metadata_df


def fetch_fastq_names(srp_accession: str, srr_accessions: []) -> {}:
    """
    Function to try and get fastq file names from the SRA database or if not available, from the ENA
    database, given a list of SRA run accessions. It also tests if the number of fastq files per run
    accession meets the hca metadata standard requirements.
    """
    """
    Takes as input a single SRA Study accession.
    """
    fastq_map = parse_reads.request_fastq_from_ENA(srp_accession)
    fastq_map = utils.test_number_fastq_files(fastq_map)
    if not fastq_map:
        """
        Takes as input a list of SRA Run accessions.
        """
        fastq_map = parse_reads.get_fastq_from_SRA(srr_accessions)
        fastq_map = utils.test_number_fastq_files(fastq_map)
    return fastq_map


def integrate_metadata(srp_metadata: pd.DataFrame,fastq_map: {},cols: []) -> pd.DataFrame:
    """
    Integrates an input dataframe including study, sample, experiment and run accessions with extracted
    fastq file names which are stored in the input fastq_map dictionary. It uses the run accessions
    (dictionary keys) to map the fastq file names to the study metadata accessions in the dataframe.
    """
    srp_metadata_update = pd.DataFrame()
    for index, row in srp_metadata.iterrows():
        srr_accession = row['Run']
        if not fastq_map or srr_accession not in fastq_map.keys():
            new_row = row.to_list()
            new_row.extend(['','',''])
            a_series = pd.Series(new_row)
            srp_metadata_update = srp_metadata_update.append(a_series, ignore_index=True)
        else:
            filenames_list = fastq_map[srr_accession]
            for file in filenames_list:
                lane_index = parse_reads.get_lane_index(file)
                if lane_index:
                    g = lane_index.group()
                    lane_index = g.split("_")[1]
                else:
                    lane_index = ''
                new_row = row.to_list()
                new_row.extend([file,parse_reads.get_file_index(file),lane_index])
                a_series = pd.Series(new_row)
                srp_metadata_update = srp_metadata_update.append(a_series, ignore_index=True)
    cols.extend(['fastq_name', 'file_index', 'lane_index'])
    srp_metadata_update.columns = cols
    return srp_metadata_update


def save_spreadsheet_to_file(workbook: Workbook, accession:str, output_dir: str):
    logging.info(f"Done. Saving workbook to excel file")
    out_file = f"{output_dir}/{accession}.xlsx"
    workbook.save(out_file)


def create_spreadsheet_using_geo_accession(accession, nthreads= 1, hca_template=DEFAULT_HCA_TEMPLATE):
    workbook = load_workbook(filename=hca_template)

    """
    Initialise a study accession string.
    """
    srp_accession = None

    """
    Check the study accession type. Is it a GEO database study accession or SRA study accession? if GEO, fetch the
    SRA study accession from the GEO accession.
    """

    if 'GSE' in accession:
        log.info(f"Fetching SRA study ID for GEO dataset {accession}")
        srp_accession = fetch_srp_accession(accession)
        log.info(f"Found SRA study ID: {srp_accession}")

    elif 'SRP' in accession or 'ERP' in accession:
        srp_accession = accession

    if not srp_accession:
        raise Exception(f"No SRA study accession is available for accession {accession}")

    else:
        """
        Fetch the SRA study metadata for the srp accession.
        """
        log.info(f"Fetching study metadata for SRA study ID: {srp_accession}")
        srp_metadata = fetch_srp_metadata(srp_accession)

        """
        Save the column names for later.
        """
        cols = srp_metadata.columns.tolist()

        """
        Fetch the fastq file names associated with the list of SRA study run accessions.
        """
        log.info(f"Fetching fastq file names for SRA study ID: {srp_accession}")
        fastq_map = fetch_fastq_names(srp_accession, list(srp_metadata['Run']))

        """
        Record whether both read1 and read2 fastq files are available for the run accessions in the study.
        """
        if not fastq_map:
            log.info(f"Both Read1 and Read2 fastq files are not available for SRA study ID: {srp_accession}")

        else:
            log.info(f"Found fastq files for SRA study ID: {srp_accession}")

        """
        Integrate metadata and fastq file names into a single dataframe.
        """
        log.info(f"Integrating study metadata and fastq file names")
        srp_metadata_update = integrate_metadata(srp_metadata, fastq_map, cols)

        """
        Get HCA Sequence file metadata: fetch as many fields as is possible using the above metadata accessions.
        """
        log.info(f"Getting Sequence file tab")
        sequence_file_tab = get_tab.get_sequence_file_tab_xls(srp_metadata_update, workbook,
                                                              tab_name="Sequence file")

        """
        Get HCA Cell suspension metadata: fetch as many fields as is possible using the above metadata accessions.
        """
        log.info(f"Getting Cell suspension tab")
        get_tab.get_cell_suspension_tab_xls(srp_metadata_update, workbook, tab_name="Cell suspension")

        """
        Get HCA Specimen from organism metadata: fetch as many fields as is possible using the above metadata accessions.
        """
        log.info(f"Getting Specimen from Organism tab")
        get_tab.get_specimen_from_organism_tab_xls(srp_metadata_update, workbook, nthreads,
                                                   tab_name="Specimen from organism")

        """
        Get HCA Library preparation protocol metadata: fetch as many fields as is possible using the above metadata accessions.
        """
        log.info(f"Getting Library preparation protocol tab")
        library_protocol_dict, attribute_lists = get_tab.get_library_protocol_tab_xls(srp_metadata_update, workbook,
                                                                                      tab_name="Library preparation protocol")

        """
        Get HCA Sequencing protocol metadata: fetch as many fields as is possible using the above metadata accessions.
        """
        log.info(f"Getting Sequencing protocol tab")
        sequencing_protocol_dict = get_tab.get_sequencing_protocol_tab_xls(workbook, attribute_lists,
                                                                           tab_name="Sequencing protocol")

        """
        Update HCA Sequence file metadata with the correct library preparation protocol ids and sequencing protocol ids.
        """
        log.info(f"Updating Sequencing file tab with protocol ids")
        get_tab.update_sequence_file_tab_xls(sequence_file_tab, library_protocol_dict, sequencing_protocol_dict,
                                             workbook, tab_name="Sequence file")

        """
        Get Project metadata: fetch as many fields as is possible using the above metadata accessions.
        """
        log.info(f"Getting project metadata")
        project_name, project_title, project_description, project_pubmed_id = get_tab.get_project_main_tab_xls(
            srp_metadata_update, workbook, accession, tab_name="Project")

        try:
            """
            Get Project - Publications metadata: fetch as many fields as is possible using the above metadata accessions.
            """
            get_tab.get_project_publication_tab_xls(workbook, tab_name="Project - Publications",
                                                    project_pubmed_id=project_pubmed_id)
        except AttributeError:
            log.info(f'Publication attribute error with GEO project {accession}')

        try:
            """
            Get Project - Contributors metadata: fetch as many fields as is possible using the above metadata accessions.
            """
            get_tab.get_project_contributors_tab_xls(workbook, tab_name="Project - Contributors",
                                                     project_pubmed_id=project_pubmed_id)
        except AttributeError:
            log.info(f'Contributors attribute error with GEO project {accession}')

        try:
            """
            Get Project - Funders metadata: fetch as many fields as is possible using the above metadata accessions.
            """
            get_tab.get_project_funders_tab_xls(workbook, tab_name="Project - Funders",
                                                project_pubmed_id=project_pubmed_id)
        except AttributeError:
            log.info(f'Funders attribute error with GEO project {accession}')
    return workbook


def create_spreadsheet_using_geo_accessions(accession_list, output_dir: str, nthreads=1,
                                            hca_template=DEFAULT_HCA_TEMPLATE):
    """
    For each study accession provided, retrieve the relevant metadata from the SRA, ENA and EuropePMC databases and write to an
    HCA metadata spreadsheet.
    """
    for accession in accession_list:
        workbook = create_spreadsheet_using_geo_accession(accession, nthreads, hca_template)
        save_spreadsheet_to_file(workbook, accession, output_dir)


def prepare_logging():
    log.basicConfig(stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        log.error("Exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def main():
    prepare_logging()
    """
    Parse user-provided command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--accession', type=str, help='accession (str): either GEO or SRA accession')
    parser.add_argument('--accession_list', type=utils.check_list_str, help='accession list (comma separated)')
    parser.add_argument('--input_file', type=utils.check_file,help='optional path to tab-delimited input .txt file')
    parser.add_argument('--nthreads', type=int, default=1,
                        help='number of multiprocessing processes to use')
    parser.add_argument('--template', default=DEFAULT_HCA_TEMPLATE,
                        help='path to an HCA spreadsheet template (xlsx)')
    parser.add_argument('--header_row', type=int, default=4,
                        help='header row with HCA programmatic names')
    parser.add_argument('--input_row1', type=int, default=6,
                        help='HCA metadata input start row')
    parser.add_argument('--output_dir', default='spreadsheets/',
                        help='path to output directory; if it does not exist, the directory will be created')
    parser.add_argument('--output_log', type=bool, default=True,
                        help='True/False: should the output result log be created')

    args = parser.parse_args()

    """
    Check user-provided command-line arguments are valid.
    """
    if args.input_file:
        accession_list = args.input_file
    elif args.accession_list:
        accession_list = args.accession_list
    elif args.accession:
        accession_list = [args.accession]
    else:
        raise ValueError("GEO or SRA accession input must be specified")

    log.info(f"Using the HCA template file specified at: {args.template}")

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    try:
        create_spreadsheet_using_geo_accessions(accession_list, args.output_dir, args.nthreads, args.template)
    except Exception:
        log.exception("")

if __name__ == "__main__":
    main()
