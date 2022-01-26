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

import re
import requests
from retry import retry


# TODO: Might be a good idea to re-visit this after a production implementation
#  of the contig-alias resolution project is available
@retry(tries=10, delay=5, backoff=1.2, jitter=(1, 3))
def resolve_contig_accession_to_chromosome_name(contig_accession, line_limit=100):
    """
    Given a Genbank contig accession, get the corresponding chromosome name from the ENA Text API
    which returns results in a EMBL Flatfile format

    :param contig_accession: Genbank contig accession (ex:  CM003032.1)
    :param line_limit: number of lines to parse in the EMBL Flatfile result to find the chromosome before giving up
    :return: Chromosome name (ex: 12 when given an accession CM003032.1)
    """
    ENA_TEXT_API_URL = "https://www.ebi.ac.uk/ena/browser/api/text/{0}?lineLimit={1}&annotationOnly=true"
    response = requests.get(ENA_TEXT_API_URL.format(contig_accession, line_limit))
    response_lines = response.content.decode("utf-8").split("\n")
    num_lines = len(response_lines)

    features_section_found, source_line_found = False, False
    chosen_response = []
    line_index = 0
    # Look for the "source" feature under the "Features" section in the text response
    while line_index < num_lines:
        line = response_lines[line_index]
        if not (features_section_found or line.lower().startswith("fh   key")):
            line_index += 1
            continue
        features_section_found = True
        # Based on "Data item positions" described here, http://www.insdc.org/files/feature_table.html#3.4.2
        # the sixth character represents the start of the feature key
        if not (source_line_found or line[5:].lower().startswith("source")):
            line_index += 1
            continue
        source_line_found = True
        if line[21:].startswith("/"):
            assembled_line = line.strip()
            line_index += 1
            # Assemble text spread across multiple lines until
            # we hit the next qualifier (starts with /) or the next section
            while line_index < num_lines and \
                    not (response_lines[line_index][21:].startswith("/")
                         or response_lines[line_index][5:6].strip() != ''):
                line = response_lines[line_index]
                assembled_line += " " + line[21:].strip()
                line_index += 1

            # Fall back to organelle in case of MT/Chloroplast accessions
            # and the reference notes in case of Linkage Group molecules
            chosen_response = re.findall('.*/chromosome=".+"', assembled_line) or \
                              re.findall('.*/organelle=".+"', assembled_line) or \
                              re.findall('.*/note=".+"', assembled_line)

            # If we have a response to give, no need to continue further
            # If the sixth character is not empty, we have reached the next feature, so no need to continue further
            if chosen_response or line[5:6].strip() != '':
                break
        else:
            line_index += 1

    if not chosen_response:
        return ""

    return str.split(chosen_response[0], '"')[1].strip()


def is_wgs_accession_format(contig_accession):
    """
    Check if a Genbank contig is part of WGS (Whole Genome Shotgun) sequence

    :param contig_accession: Genbank contig accession (ex:  CM003032.1)
    :return: True if the provided contig is in the WGS format
    """
    wgs_prefix = contig_accession[:4]
    wgs_numeric_suffix = contig_accession[4:].replace(".", "")
    return str.isalpha(wgs_prefix) and str.isnumeric(wgs_numeric_suffix)


def get_chromosome_name_for_contig_accession(contig_accession):
    """
    Given a Genbank contig accession, get the corresponding chromosome name

    :param contig_accession: Genbank contig accession (ex:  CM003032.1)
    :return: Chromosome name (ex: 12 when given an accession CM003032.1)
    """

    # Don't bother calling the ENA web service to get the chromosome number if the accession is a WGS accession
    # since the API will proceed to download the entire WGS dataset which can be in hundreds of MBs or even GBs
    # See https://www.ebi.ac.uk/ena/browser/api/text/AABR07050911.1?lineLimit=100&annotationOnly=true for example
    if is_wgs_accession_format(contig_accession):
        return None

    return \
        resolve_contig_accession_to_chromosome_name(contig_accession, 1000) or \
        resolve_contig_accession_to_chromosome_name(contig_accession, 10000) or \
        resolve_contig_accession_to_chromosome_name(contig_accession, 100000)
