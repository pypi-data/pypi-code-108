# --- core imports
from time import sleep
import xml.etree.ElementTree as xm

# --- third-party imports
import pandas as pd
from pysradb.sraweb import SRAweb
import requests as rq

# ---application imports
from geo_to_hca.utils import handle_errors


"""
Define constants.
"""
STATUS_ERROR_CODE = 400

"""
Define functions.
"""
class SraUtils:
    """
    Class to handle requests from NCBI SRA database via SRAweb() or NCBI eutils.
    """
    def get_srp_accession_from_geo(geo_accession: str) -> str:
        """
        Function to retrieve an SRA database study accession for a given input GEO accession.
        """
        sleep(0.5)
        try:
            srp = SRAweb().gse_to_srp(geo_accession)
        except:
            srp = None
        if not isinstance(srp, pd.DataFrame):
            srp = None
        elif isinstance(srp, pd.DataFrame):
            if srp.shape[0] == 0:
                srp = None
            else:
                srp = srp
        return srp

    def get_srp_metadata(srp_accession: str) -> pd.DataFrame:
        """
        Function to retrieve a dataframe with multiple lists of experimental and sample accessions
        associated with a particular SRA study accession from the SRA database.
        """
        sleep(0.5)
        srp_metadata_url = f'http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=runinfo&term={srp_accession}'
        return pd.read_csv(srp_metadata_url)

    def parse_xml_SRA_runs(xml_content: object) -> object:
        for experiment_package in xml_content.findall('EXPERIMENT_PACKAGE'):
            yield experiment_package

    def request_fastq_from_SRA(srr_accessions: []) -> object:
        """
        Function to retrieve an xml file containing information associated with a list of NCBI SRA run accessions.
        In particular, the xml contains the paths to the data (if available) in fastq or other format.
        """
        sleep(0.5)
        url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch/fcgi?db=sra&id={",".join(srr_accessions)}'
        srr_metadata_url = rq.get(url)
        if srr_metadata_url.status_code == STATUS_ERROR_CODE:
            raise handle_errors.NotFoundSRA(srr_metadata_url, srr_accessions)
        try:
            xml_content = xm.fromstring(srr_metadata_url.content)
        except:
            xml_content = None
        return xml_content

    def request_accession_info(accessions: [],accession_type: str) -> object:
        """
        Function which sends a request to NCBI SRA database to get an xml file with metadata about a
        given list of biosample or experiment accessions. The xml contains various metadata fields.
        """
        if accession_type == 'biosample':
            url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch/fcgi?db=biosample&id={",".join(accessions)}'
        if accession_type == 'experiment':
            url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch/fcgi?db=sra&id={",".join(accessions)}'
        sra_url = rq.get(url)
        if sra_url.status_code == STATUS_ERROR_CODE:
            raise handle_errors.NotFoundSRA(sra_url, accessions)
        return xm.fromstring(sra_url.content)

    def request_bioproject_metadata(bioproject_accession: str):
        """
        Function to request metadata at the project level given an SRA Bioproject accession.
        """
        sleep(0.5)
        srp_bioproject_url = rq.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch/fcgi?db=bioproject&id={bioproject_accession}')
        if srp_bioproject_url.status_code == STATUS_ERROR_CODE:
            raise handle_errors.NotFoundSRA(srp_bioproject_url, bioproject_accession)
        return xm.fromstring(srp_bioproject_url.content)

    def request_pubmed_metadata(project_pubmed_id: str):
        """
        Function to request metadata at the publication level given a pubmed ID.
        """
        sleep(0.5)
        pubmed_url = rq.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch/fcgi?db=pubmed&id={project_pubmed_id}&rettype=xml')
        if pubmed_url.status_code == STATUS_ERROR_CODE:
            raise handle_errors.NotFoundSRA(pubmed_url, project_pubmed_id)
        return xm.fromstring(pubmed_url.content)
