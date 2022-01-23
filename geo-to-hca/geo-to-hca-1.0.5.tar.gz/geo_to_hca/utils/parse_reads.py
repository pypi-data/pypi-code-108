# --- core imports
import logging
import re

# --- third-party imports
import pandas as pd
import urllib.parse

# ---application imports
from geo_to_hca.utils import sra_utils

log = logging.getLogger(__name__)


def request_fastq_from_ENA(srp_accession: str) -> {}:
    """
    Function to retrieve fastq file paths from ENA given an SRA study accession. The request returns a
    dataframe with a list of run accessions and their associated fastq file paths. The multiple file paths for
    each run are stored in a single string. This string is then stored in a dictionary with the associated
    run accessions as keys.
    """
    try:
        params = {
            'accession': srp_accession,
            'result': 'read_run',
            'fields': 'run_accession,fastq_ftp'
        }
        request_params_str = urllib.parse.urlencode(params)
        file_report_url = f'https://www.ebi.ac.uk/ena/portal/api/filereport?{request_params_str}'
        fastq_results = pd.read_csv(file_report_url, delimiter='\t')
        run_accessions = list(fastq_results['run_accession'])
        ftps = list(fastq_results['fastq_ftp'])
        fastq_map = {run_accessions[i]: extract_reads_ENA(ftps[i]) for i in range(0, len(run_accessions))}
        return fastq_map
    except Exception as e:
        log.exception(e)
        return None


def extract_reads_ENA(ftp_path: str) -> []:
    """
    Function to extract single fastq file names from a string containing multiple fastq file paths.
    """
    try:
        read_files = ftp_path.split(';')
        read_files = [file.split("/")[-1] for file in read_files]
    except:
        read_files = []
    return read_files

def extract_reads_SRA(read_values:str,accession:str,fastq_map:{}) -> {}:
    """
    Function to extract a list of fastq file names from a str containing multiple file paths associated
    with a single run accession.
    """
    if "--read1PairFiles" not in read_values or "--read2PairFiles" not in read_values:
        return fastq_map
    else:
        read_info_list = read_values.strip().split('--')[1:]
        for read_info in read_info_list:
            read_info = read_info.strip()
            split_read = read_info.split("=")
            if 'fastq.gz' in split_read[1]:
                if accession in fastq_map.keys():
                    fastq_map[accession].append(split_read[1])
                else:
                    fastq_map[accession] = [split_read[1]]
    return fastq_map

def get_file_names_from_SRA(experiment_package: object) -> {}:
    """
    Gets fastq file names from an xml returned from SRA following a request with a list
    of run accessions.
    """
    fastq_map = {}
    run_set = experiment_package.find('RUN_SET')
    for run in run_set:
        try:
            accession = run.attrib['accession']
            run_attributes = run.find('RUN_ATTRIBUTES')
            for attribute in run_attributes:
                if attribute.find('TAG').text == 'options':
                    read_values = attribute.find('VALUE').text
                    fastq_map = extract_reads_SRA(read_values,accession,fastq_map)
        except:
            continue
    return fastq_map

def get_fastq_from_SRA(srr_accessions: []) -> {}:
    """
    Function to parse the xml output following a request for run accession metadata to the NCBI SRA database.
    A list of SRA run accessions is given as input to the request. The fastq file paths are extracted from
    this xml and the file names are added to a dictionary with the associated run accessions as keys (fastq_map).
    """
    xml_content = sra_utils.SraUtils.request_fastq_from_SRA(srr_accessions)
    if not xml_content:
        fastq_map = None
    else:
        experiment_packages = sra_utils.SraUtils.parse_xml_SRA_runs(xml_content)
        for experiment_package in experiment_packages:
            try:
                fastq_map = get_file_names_from_SRA(experiment_package)
            except:
                continue
    return fastq_map

def get_lane_index(file: str) -> str:
    """
    Looks for a lane index inside a fastq file name and returns the lane index if found.
    """
    result = re.search('_L[0-9]{3}', file)
    return result

def get_file_index(file: str) -> str:
    """
    Looks for a read index inside a fastq file name (R1,R2,I1,etc.). Returns the read index if found.
    """
    if "_I1" in file or "_R3" in file or "_3" in file:
        ind = 'index1'
    elif "_R1" in file or "_1" in file:
        ind = 'read1'
    elif "_R2" in file or "_2" in file:
        ind = 'read2'
    elif "_I2" in file or "_R4" in file or "_4" in file:
        ind = 'index2'
    else:
         ind = ''
    return ind
