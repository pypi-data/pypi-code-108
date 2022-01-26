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


class NCBIAssembly(AppLogger):
    """
    Class that represent an assembly that would originate from NCBI data
    It takes a GCA or GCF accession and can download the assembly report and genomics fasta.
    Using species_scientific_name and assembly_accession it create a directory structure in the provided
    reference_directory:
        - species_scientific_name1
            - assembly_accession1
            - assembly_accession2
        - species_scientific_name2
    the eutils_api_key is only used to retrieve additional contigs if required.
    """

    def __init__(self, assembly_accession, species_scientific_name, reference_directory, eutils_api_key=None):
        self.check_assembly_accession_format(assembly_accession)
        self.assembly_accession = assembly_accession
        self.species_scientific_name = species_scientific_name
        self.reference_directory = reference_directory
        self.eutils_api_key = eutils_api_key

    @staticmethod
    def is_assembly_accession_format(assembly_accession):
        if re.match(r"^GC[F|A]_\d+\.\d+$", assembly_accession) is not None:
            return True
        return False

    @staticmethod
    def check_assembly_accession_format(assembly_accession):
        if not NCBIAssembly.is_assembly_accession_format(assembly_accession):
            raise ValueError(f'Invalid assembly accession: {assembly_accession} it has to be in the form of '
                            'GCF_XXXXXXXXX.X or GCA_XXXXXXXXX.X where X is a number')

    @property
    def assembly_directory(self):
        assembly_directory = os.path.join(
            self.reference_directory,  self.species_scientific_name.lower().replace(' ', '_'), self.assembly_accession
        )
        os.makedirs(assembly_directory, exist_ok=True),
        return assembly_directory

    @property
    def assembly_report_path(self):
        return os.path.join(self.assembly_directory, self.assembly_accession + '_assembly_report.txt')

    @property
    def assembly_fasta_path(self):
        return os.path.join(self.assembly_directory, self.assembly_accession + '.fa')

    @property
    def assembly_compressed_fasta_path(self):
        return os.path.join(self.assembly_directory, self.assembly_accession + '.fa.gz')

    @retry(tries=4, delay=2, backoff=1.2, jitter=(1, 3))
    def _download_file(self, destination_file, url):
        self.info('Download assembly file for %s to %s', self.assembly_accession, destination_file)
        request.urlretrieve(url, destination_file)
        request.urlcleanup()

    @cached_property
    def _ncbi_genome_folder_url_and_content(self):
        """
        Internal property that retrieve and store the NCBI ftp url and content of the genome folder.
        """
        ftp = FTP('ftp.ncbi.nlm.nih.gov', timeout=600)
        ftp.login('anonymous', 'anonymous')
        genome_folder = 'genomes/all/' + '/'.join([self.assembly_accession[0:3], self.assembly_accession[4:7],
                                                   self.assembly_accession[7:10],
                                                   self.assembly_accession[10:13]]) + '/'
        ftp.cwd(genome_folder)
        all_genome_subfolders = []
        ftp.retrlines('NLST', lambda line: all_genome_subfolders.append(line))

        genome_subfolders = [folder for folder in all_genome_subfolders if folder == self.assembly_accession]
        if len(genome_subfolders) != 1:
            self.debug('Cannot find good match for accession folder with "%s": %s match found', self.assembly_accession, len(genome_subfolders))
            genome_subfolders = [folder for folder in all_genome_subfolders if folder.startswith(self.assembly_accession + '_')]
        if len(genome_subfolders) != 1:
            self.debug('Cannot find good match for accession folder with "starting with %s_": %s match found', self.assembly_accession, len(genome_subfolders))
            genome_subfolders = [folder for folder in all_genome_subfolders if folder.startswith(self.assembly_accession)]
        if len(genome_subfolders) != 1:
            self.debug('Cannot find good match for accession folder with "starting with %s": %s match found', self.assembly_accession, len(genome_subfolders))
            genome_subfolders = [folder for folder in all_genome_subfolders if self.assembly_accession in folder]
        if len(genome_subfolders) != 1:
            self.debug('Cannot find good match for accession folder with "%s in name": %s match found', self.assembly_accession, len(genome_subfolders))
            raise Exception('more than one folder matches the assembly accession: ' + str(genome_subfolders))
        ftp.cwd(genome_subfolders[0])
        genome_files = []
        ftp.retrlines('NLST', lambda line: genome_files.append(line))
        url = 'ftp://' + 'ftp.ncbi.nlm.nih.gov' + '/' + genome_folder + genome_subfolders[0]
        ftp.close()
        return url, genome_files

    @cached_property
    def assembly_report_url(self):
        """
        Search on the NCBI FTP for the assembly report file and return the full url if only one found.
        Raise if not.
        """
        url, genome_files = self._ncbi_genome_folder_url_and_content
        assembly_reports = [genome_file for genome_file in genome_files if 'assembly_report.txt' in genome_file]
        if len(assembly_reports) != 1:
            raise Exception('more than one file has "assembly_report" in its name: ' + str(assembly_reports))
        return url + '/' + assembly_reports[0]

    @cached_property
    def assembly_fasta_url(self):
        """
        Search on the NCBI FTP for the assembly genomics fasta file and return the full url if only one found.
        Raise if not.
        """
        url, genome_files = self._ncbi_genome_folder_url_and_content
        assembly_fasta = [genome_file for genome_file in genome_files if genome_file.endswith('_genomic.fna.gz')]
        # Remove the entries that are from genomics dna but the whole genome
        assembly_fasta = [fasta for fasta in assembly_fasta if '_from_' not in fasta]
        if len(assembly_fasta) > 1:
            raise Exception('{} file found ending with "_genomic.fna.gz" in its name: {}'.format(len(assembly_fasta),
                                                                                                 assembly_fasta))
        return url + '/' + assembly_fasta[0]

    def get_assembly_report_rows(self):
        """Download the assembly report if it does not exist then parse it to create a generator
        that return each row as a dict."""
        self.download_assembly_report()
        with open(self.assembly_report_path) as open_file:
            headers = None
            # Parse the assembly report file to find the header then stop
            for line in open_file:
                if line.lower().startswith("# sequence-name") and "sequence-role" in line.lower():
                    headers = line.strip().split('\t')
                    break
            reader = DictReader(open_file, fieldnames=headers, dialect=excel_tab)
            for record in reader:
                yield record

    def download_assembly_report(self, overwrite=False):
        if not os.path.isfile(self.assembly_report_path) or overwrite:
            self._download_file(self.assembly_report_path, self.assembly_report_url)

    def download_assembly_fasta(self, overwrite=False):
        if not os.path.isfile(self.assembly_fasta_path) or overwrite:
            self._download_file(self.assembly_compressed_fasta_path, self.assembly_fasta_url)
            run_command_with_output(
                'Uncompress {}'.format(self.assembly_compressed_fasta_path),
                'gunzip -f {}'.format(self.assembly_compressed_fasta_path)
            )

    def construct_fasta_from_report(self, genbank_only=False):
        """
        Download the assembly report if it does not exist then create the assembly fasta from the contig.
        If the assembly already exist then it only add any missing contig.
        """
        written_contigs = self.get_written_contigs(self.assembly_fasta_path)
        contig_to_append = []
        for row in self.get_assembly_report_rows():
            genbank_accession = row['GenBank-Accn']
            refseq_accession = row['RefSeq-Accn']
            relationship = row['Relationship']
            accession = genbank_accession
            if relationship != '=' and genbank_accession == 'na' and not genbank_only:
                accession = refseq_accession
            if accession in written_contigs:
                self.debug('Accession ' + accession + ' already in the FASTA file, don\'t need to be downloaded')
                continue
            if not accession or accession == 'na':
                raise ValueError('Accession {} found in report is not valid'.format(accession))
            contig_to_append.append(self.download_contig_sequence_from_ncbi(accession))

        # Now append all the new contigs to the existing fasta
        with open(self.assembly_fasta_path, 'a+') as fasta:
            for contig_path in contig_to_append:
                with open(contig_path) as sequence:
                    for line in sequence:
                        # Check that the line is not empty
                        if line.strip():
                            fasta.write(line)
                os.remove(contig_path)

    def download_contig_sequence_from_ncbi(self, accession):
        sequence_tmp_path = os.path.join(self.assembly_directory, accession + '.fa')
        self.download_contig_from_ncbi(accession, sequence_tmp_path)
        self.info(accession + " downloaded and added to FASTA sequence")
        return sequence_tmp_path

    @staticmethod
    def get_written_contigs(fasta_path):
        written_contigs = []
        match = re.compile(r'>(.*?)\s')
        if os.path.isfile(fasta_path):
            with open(fasta_path, 'r') as file:
                for line in file:
                    written_contigs.extend(match.findall(line))
        return written_contigs

    @retry(tries=4, delay=2, backoff=1.2, jitter=(1, 3))
    def download_contig_from_ncbi(self, contig_accession, output_file):
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

    def download_or_construct(self, genbank_only=False, overwrite=False):
        """First download the assembly report and fasta from the FTP, then append any missing contig from
        the assembly report to the assembly fasta."""
        self.download_assembly_report(overwrite)
        try:
            self.download_assembly_fasta(overwrite)
        except:
            pass
        # This will either confirm the presence of all the contig or download any one missing
        self.construct_fasta_from_report(genbank_only)
