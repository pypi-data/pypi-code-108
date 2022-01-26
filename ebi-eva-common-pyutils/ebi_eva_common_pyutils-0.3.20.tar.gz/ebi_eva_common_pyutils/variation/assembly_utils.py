# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ftplib import FTP
import http
import re
import requests

from ebi_eva_common_pyutils.assembly import NCBIAssembly
from ebi_eva_common_pyutils.logger import logging_config as log_cfg

EUTILS_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
ESEARCH_URL = EUTILS_URL + 'esearch.fcgi'
ESUMMARY_URL = EUTILS_URL + 'esummary.fcgi'
EFETCH_URL = EUTILS_URL + 'efetch.fcgi'


logger = log_cfg.get_logger(__name__)


def retrieve_genbank_assembly_accessions_from_ncbi(assembly_txt):
    """
    Attempt to find any assembly genebank accession base on a free text search.
    """
    assembly_accessions = set()
    payload = {'db': 'Assembly', 'term': '"{}"'.format(assembly_txt), 'retmode': 'JSON'}
    data = requests.get(ESEARCH_URL, params=payload).json()
    if data and data.get('esearchresult', {}).get('idlist'):
        assembly_id_list = data.get('esearchresult').get('idlist')
        payload = {'db': 'Assembly', 'id': ','.join(assembly_id_list), 'retmode': 'JSON'}
        summary_list = requests.get(ESUMMARY_URL, params=payload).json()
        for assembly_id in summary_list.get('result', {}).get('uids', []):
            assembly_info = summary_list.get('result').get(assembly_id)
            if 'genbank' in assembly_info['synonym']:
                assembly_accessions.add(assembly_info['synonym']['genbank'])
    if len(assembly_accessions) != 1:
        logger.warning('%s Genbank synonyms found for assembly %s ', len(assembly_accessions), assembly_txt)
    return list(assembly_accessions)


def retrieve_genbank_equivalent_for_GCF_accession(assembly_accession):
    genbank_synonyms = retrieve_genbank_assembly_accessions_from_ncbi(assembly_accession)
    if len(genbank_synonyms) != 1:
        raise ValueError('%s Genbank synonyms found for assembly %s ' % (len(genbank_synonyms), assembly_accession))
    return genbank_synonyms.pop()


def resolve_assembly_name_to_GCA_accession(assembly_name):
    ENA_ASSEMBLY_NAME_QUERY_URL = "https://www.ebi.ac.uk/ena/portal/api/search" \
                                  "?result=assembly&query=assembly_name%3D%22{0}%22&format=json".format(assembly_name)
    response = requests.get(ENA_ASSEMBLY_NAME_QUERY_URL)
    if response.status_code == http.HTTPStatus.OK.value:
        response_json = response.json()
        if len(response_json) == 0:
            raise ValueError("Could not resolve assembly name {0} to a GCA accession!".format(assembly_name))
        elif len(response_json) > 1:
            raise ValueError("Assembly name {0} resolved to more than one GCA accession!".format(assembly_name))
        else:
            return response.json()[0]["accession"] + "." + response.json()[0]["version"]
    else:
        raise ValueError("Could not resolve assembly name {0} to a GCA accession!".format(assembly_name))


def get_assembly_report_url(assembly_accession):
    return NCBIAssembly(assembly_accession).assembly_report_url
