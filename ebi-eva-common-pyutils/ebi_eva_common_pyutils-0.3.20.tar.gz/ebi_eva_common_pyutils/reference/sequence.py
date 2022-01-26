# Copyright 2019 EMBL - European Bioinformatics Institute
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
import os
import urllib
from csv import DictReader, excel_tab
from ftplib import FTP
import re
from urllib import request

from cached_property import cached_property
from retry import retry

from ebi_eva_common_pyutils.command_utils import run_command_with_output
from ebi_eva_common_pyutils.logger import AppLogger


class NCBISequence(AppLogger):
    """
    Class that represent an Sequence that would originate from NCBI data
    It takes a any Genbank or refseq accession and can download the sequence genomics fasta form.
    Using species_scientific_name and assembly_accession it create a directory structure in the provided
    reference_directory:
        - species_scientific_name1
            - assembly_accession1
            - assembly_accession2
        - species_scientific_name2
    """

    insdc_accession_formats = [
        r'[A-Z][0-9]{5}\.[0-9]+',
        r'[A-Z]{2}[0-9]{6}\.[0-9]+',
        r'[A-Z]{2}[0-9]{8}\.[0-9]+',
        r'[A-Z]{4}[0-9]{8}\.[0-9]+',
        r'[A-Z]{6}[0-9]{9}\.[0-9]+'
    ]

    def __init__(self, sequence_accession, species_scientific_name, reference_directory, eutils_api_key=None):
        self.sequence_accession = sequence_accession
        self.species_scientific_name = species_scientific_name
        self.reference_directory = reference_directory
        self.eutils_api_key = eutils_api_key

    @staticmethod
    def is_genbank_accession_format(accession):
        if any(
                re.match(insdc_accession_format, accession)
                for insdc_accession_format in NCBISequence.insdc_accession_formats
        ):
            return True
        return False

    @staticmethod
    def check_genbank_accession_format(accession):
        if not NCBISequence.is_genbank_accession_format(accession):
            raise ValueError('Invalid INSDC accession: %s' % accession)

    @property
    def sequence_directory(self):
        sequence_directory = os.path.join(
            self.reference_directory,  self.species_scientific_name.lower().replace(' ', '_'), self.sequence_accession
        )
        os.makedirs(sequence_directory, exist_ok=True),
        return sequence_directory

    @property
    def sequence_fasta_path(self):
        return os.path.join(self.sequence_directory, self.sequence_accession + '.fa')

    def download_contig_sequence_from_ncbi(self, genbank_only=True):
        if genbank_only:
            self.check_genbank_accession_format(self.sequence_accession)
        self._download_contig_from_ncbi(self.sequence_accession, self.sequence_fasta_path)
        self.info(self.sequence_fasta_path + " downloaded and added to FASTA sequence")

    @retry(tries=4, delay=2, backoff=1.2, jitter=(1, 3))
    def _download_contig_from_ncbi(self, contig_accession, output_file):
        parameters = {
            'db': 'nuccore',
            'id': contig_accession,
            'rettype': 'fasta',
            'retmode': 'text',
            'tool': 'eva',
            'email': 'eva-dev@ebi.ac.uk'
        }
        if self.eutils_api_key:
            parameters['api_key'] = self.eutils_api_key
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urllib.parse.urlencode(parameters)
        self.info('Downloading ' + contig_accession)
        urllib.request.urlretrieve(url, output_file)

