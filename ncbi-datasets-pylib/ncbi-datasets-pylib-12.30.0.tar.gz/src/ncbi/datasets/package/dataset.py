"""Representations of a downloaded NCBI Datasets Package.

NCBI Datasets provides data in ZipArchives for Genome, Gene, Pathogen and Virus resources.
These classes each contain dataset catalogs that help programmatically determine
the file contents.

Examples:
    A quickstart is to download a package, and then create a generic `Dataset` wrapper:

    >>> from ncbi.datasets.package.dataset import get_dataset_from_file

    package = get_dataset_from_file(path_to_file)
    for report in package.get_data_reports():
        # do something with the protobuf report object

"""
import contextlib
import json
import logging
import os
import io
from typing import Any, Dict, List, TextIO, Iterator, Set, Tuple
import zipfile
import jsonlines

from google.protobuf.json_format import ParseDict
from google.protobuf.json_format import ParseError
from google.protobuf.json_format import SerializeToJsonError

import ncbi.datasets.v1.reports.assembly_pb2 as assembly_report_pb2
import ncbi.datasets.v1.reports.assembly_sequence_info_pb2 as sequence_report_pb2
import ncbi.datasets.v1.reports.gene_pb2 as gene_report_pb2
import ncbi.datasets.v1.reports.virus_pb2 as virus_report_pb2
import ncbi.datasets.v1.reports.microbigge_pb2 as microbigge_report_pb2

logger = logging.getLogger(__name__)


def get_dataset_from_file(zip_file_or_directory: str, dataset_type: str) -> "Dataset":
    """Create a Dataset-derived object of type 'dataset_type' and return it.

    Returns:
        A subclass of the class 'Dataset' as specified by the caller.
    """

    if dataset_type == "ASSEMBLY":
        return AssemblyDataset(zip_file_or_directory)
    elif dataset_type == "GENE":
        return GeneDataset(zip_file_or_directory)
    elif dataset_type == "VIRUS":
        return VirusDataset(zip_file_or_directory)
    elif dataset_type == "MICROBIGGE":
        return MicrobiggeDataset(zip_file_or_directory)
    raise ValueError(dataset_type)


def _get_files_of_type(elt: Dict[str, Any], file_type: str, results: List[str]) -> None:
    """Recursively search through dictionary 'elt' for files of type 'file_type'.

    Returns:
        A list of file paths for any files of type 'file_type'
    """

    if isinstance(elt, dict):
        for k, v in elt.items():
            if k == "files" and isinstance(v, list):
                results.extend([f["filePath"] for f in v if f["fileType"] == file_type])
            else:
                _get_files_of_type(v, file_type, results)
    elif isinstance(elt, list):
        for v in elt:
            _get_files_of_type(v, file_type, results)


def _get_file_types(elt: Dict[str, Any], results: Set[str]) -> None:
    """Recursively search through dictionary for all file types

    Returns:
        A set of all unique file types in the dictionary 'elt'.
    """

    if isinstance(elt, dict):
        for k, v in elt.items():
            if k == "files" and isinstance(v, list):
                results.update([f["fileType"] for f in v])
            else:
                _get_file_types(v, results)
    elif isinstance(elt, list):
        for v in elt:
            _get_file_types(v, results)


class Dataset:
    """Base class to extract files from datasets package

    Functions to extract files from a datasets package based on file names and types
    in the packages catalog file
    """

    def __init__(self, zipfile_or_directory: str):
        """Initialize the object with a zip file OR directory name.

        Parameters:
            zipfile_or_directory: A file or directory name.  A file is assumed to be a zip
                                  file and a directory is assumed to be the top-level
                                  directory of an unzipped datasets package.
        """

        # Zip file object - 'None' if dataset is not stored in a zip file
        self.dataset_zip = None
        # If data is stored in a zip file this is the data directory within the zip file
        # (ncbi_dataset/data), otherwise it's the full data directory path.
        self.dataset_dir = None

        if os.path.isdir(zipfile_or_directory):
            self.dataset_dir = os.path.join(zipfile_or_directory, "data")
        elif os.path.isfile(zipfile_or_directory):
            try:
                self.dataset_zip = zipfile.ZipFile(zipfile_or_directory)  # pylint:disable=consider-using-with
                self.dataset_dir = "ncbi_dataset/data"
            except zipfile.BadZipFile as e:
                logger.error("Bad zipfile: %s", e)
        else:
            logger.error("Invalid file or directory %s", zipfile_or_directory)

    # True if Dataset is reading directly from a zip file
    def is_zipped(self) -> bool:
        """Return True if the dataset is stored in a zip file"""
        return bool(self.dataset_zip)

    # Return top-level data directory
    def get_file_root_dir(self) -> str:
        """Return the data directory within the dataset (e.g. ncbi_dataset/data)"""

        return self.dataset_dir

    # return json catalog from zip file
    def get_catalog(self) -> Dict[str, Any]:
        """Return the datasets file catalog as a dictionary"""

        dataset_catalog: Dict[str, Any]
        catalog_file = self.get_file_content("dataset_catalog.json")
        if catalog_file:
            try:
                dataset_catalog = json.loads(catalog_file)
            except json.JSONDecodeError as e:
                logger.error("Error decoding dataset_catalog file to json: %s", e)
        return dataset_catalog

    def get_file_names_by_type(self, file_type: str) -> List[str]:
        """Return names of all files of type 'file_type', e.g. 'PROTEIN_FASTA'"""

        results = []
        catalog = self.get_catalog()
        _get_files_of_type(catalog, file_type, results)
        return results

    def get_files_by_type(self, file_type: str) -> Iterator[Tuple[str, str]]:
        """Return contents of all files of type 'file_type' along with their names"""

        names = self.get_file_names_by_type(file_type)
        for name in names:
            yield (self.get_file_content(name), name)

    def get_file_handles_by_type(self, file_type: str) -> Iterator[Tuple[TextIO, str]]:
        """Return file handles for all files of type 'file_type' along with their names"""

        names = self.get_file_names_by_type(file_type)
        for name in names:
            with self.get_file_handle(name) as fh:
                yield fh, name

    def get_file_types(self) -> List[str]:
        """Return all file types available in the current dataset"""

        results = set()
        catalog = self.get_catalog()
        _get_file_types(catalog, results)
        return results

    def get_file_content(self, file_name: str) -> str:
        """Return full text of file 'file_name'"""
        with self.get_file_handle(file_name) as fh:
            if not fh:
                return ""
            return fh.read()

    @contextlib.contextmanager
    def get_file_handle(self, file_name: str) -> TextIO:
        """Get handle of file using name within dataset directory

        Parameters:
            file_name: Name of file within the data directory, e.g. if the full
                       datasets path is ncbi_dataset/data/GCF_000001405.39/chrX.fna,
                       file_name should be GCF_000001405.39/chrX.fna
        Returns:
            Handle to the specified file
        """

        if self.dataset_zip:
            try:
                zinfo = self.dataset_zip.getinfo(os.path.join(self.dataset_dir, file_name))
                with io.TextIOWrapper(self.dataset_zip.open(zinfo), encoding="utf8") as fh:
                    yield fh
            except KeyError as e:
                logger.error("File %s not found in zipfile: %s", file_name, e)
        elif self.dataset_dir:
            file_path = os.path.join(self.dataset_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf8") as fh:
                    yield fh
            else:
                logger.error("File not found in datasets directory: %s", file_path)
        else:
            logger.error("Dataset not available - unable to load: %s", file_name)

    def stream_reports(self, file_type: str, protobuf_report_type: Any) -> Any:
        """Retrieve report records defined via protobuf schema from jsonl files.

        Parameters:
            file_type: The type of file from the dataset catalog, e.g.
                       'DATA_REPORT' or 'SEQUENCE_REPORT'.
            protobuf_report_type: Schema, defined using GRPC protobuf, for the
                                  current dataset and file type.

        Returns:
            Yields a set of protobuf objects for the dataset and file type.
        """

        files = self.get_file_names_by_type(file_type)
        for file in files:
            with self.get_file_handle(file) as fh:
                reader = jsonlines.Reader(fh)
                for json_dict in reader.iter(type=dict, skip_invalid=True):
                    try:
                        protobuf_rpt = protobuf_report_type()
                        ParseDict(json_dict, protobuf_rpt, ignore_unknown_fields=False)
                        yield protobuf_rpt
                    except (SerializeToJsonError, ParseError) as e:
                        logger.error("Error converting json to schema: %s", e)


class AssemblyDataset(Dataset):
    """Retrieve Assembly reports

    Methods to read Assembly and Assembly Sequence reports
    """

    def get_data_reports(self) -> Iterator[assembly_report_pb2.AssemblyDataReport]:
        """Retrieve assembly reports

        Returns:
          Yields a set of AssemblyDataReport protobuf objects
        """
        yield from self.stream_reports("DATA_REPORT", assembly_report_pb2.AssemblyDataReport)

    def get_sequence_reports(self) -> Iterator[sequence_report_pb2.SequenceInfo]:
        """Retrieve assembly sequence reports

        Returns:
          Yields a set of Assembly SequenceInfo protobuf objects
        """
        yield from self.stream_reports("SEQUENCE_REPORT", sequence_report_pb2.SequenceInfo)


class GeneDataset(Dataset):
    """Retrieve Gene reports

    Methods to read Gene reports
    """

    def get_data_reports(self) -> Iterator[gene_report_pb2.GeneDescriptor]:
        """Retrieve a gene report object

        Returns:
           Yields a set of GeneDescriptor protobuf objects
        """
        yield from self.stream_reports("DATA_REPORT", gene_report_pb2.GeneDescriptor)


class VirusDataset(Dataset):
    """Retrieve Virus reports

    Methods to read Virus reports
    """

    def get_data_reports(self) -> Iterator[virus_report_pb2.VirusAssembly]:
        """Retrieve virus assembly objects

        Returns:
          Yields a set of virus assembly report protobuf objects
        """
        yield from self.stream_reports("DATA_REPORT", virus_report_pb2.VirusAssembly)


class MicrobiggeDataset(Dataset):
    """Retrieve MicroBiggee pathogen reports

    Methods to read MicroBiggee reports
    """

    def get_data_reports(self) -> Iterator[microbigge_report_pb2.MicroBiggeReport]:
        """Retrieve MicroBigge data report objects

        Returns:
          Yields a set of MicroBigge report protobuf objects
        """
        yield from self.stream_reports("DATA_REPORT", microbigge_report_pb2.MicroBiggeReport)
