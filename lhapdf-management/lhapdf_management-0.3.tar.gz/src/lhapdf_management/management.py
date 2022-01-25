"""
    LHAPDF management library
"""
import csv
import tempfile
import tarfile
from pathlib import Path
import logging

from .configuration import environment
from .pdfsets import SetInfo
from .net_utilities import download_magic

# Set up the logger
logger = logging.getLogger(__name__)

### Listing utilities
def get_reference_list(filepath=None):
    """Reads reference file and returns list of SetInfo objects.

    The reference file is space-delimited cvs with columns:
        id_code version name

    Returns a list of SetInfo objects
    """
    if filepath is None:
        filepath = environment.datapath / environment.index_filename
    filepath = Path(filepath)
    database = []
    if not filepath.exists():
        raise ValueError(f"Could not find {filepath}")

    with filepath.open("r") as csv_file:
        logger.debug("Reading %s", filepath)
        try:
            reader = csv.reader(csv_file, delimiter=" ", skipinitialspace=True, strict=True)
            for row in reader:
                if len(row) == 3:
                    id_code, name, version = int(row[0]), str(row[1]), int(row[2])
                elif len(row) == 2:
                    # For LHAPDF <= 6.0.5
                    id_code, name, version = int(row[0]), str(row[1]), None
                else:
                    raise ValueError(f"Reference file {filepath} should have exactly 3 columns")
                database.append(SetInfo(name, id_code, version))
        except csv.Error as e:
            logger.error("Corrupted file on line %d: %s", reader.line_num, filepath)
            raise e
    return database


def get_installed_list():
    """Returns a list of SetInfo objects representing installed PDF sets."""
    lhapdf_data_folder = environment.datapath
    reference_pdf_list = get_reference_list(lhapdf_data_folder / environment.index_filename)
    reference_pdfs = {s.name: s for s in reference_pdf_list}
    # Walk down the list of .info files and get only the ones installed
    pdf_iterator = lhapdf_data_folder.glob("*/*.info")
    return [reference_pdfs[pdf.stem] for pdf in pdf_iterator if pdf.stem in reference_pdfs]


#####


def update_reference_file():
    """Update the reference file"""
    if download_magic(environment.index_filename, environment.datapath):
        return True
    logger.error("Unable to update the index reference file")
    return False


def install_pdf(name, dry=False, upgrade=False, keep=False):
    """Install the named pdf
    Don't install if the PDF already exists (unless upgrade=True)
    If keep is true, do not remove the tarball.
    If dry is true, skip the download (and extract) step
    """
    if not upgrade:
        final_folder = environment.datapath / name
        if final_folder.exists():
            logger.error("The PDF %s already exists at %s", name, environment.datapath)
            return False

    tarname = f"{name}.tar.gz"
    tmp_folder = Path(tempfile.mkdtemp())
    if download_magic(tarname, tmp_folder, dry=dry):
        if dry:
            return True
        extract_tarball(tmp_folder / tarname, environment.datapath, keep_tarball=keep)
        return True
    logger.error("Unable to download the %s PDF", name)
    return False


def extract_tarball(tar_filename, dest_dir, keep_tarball=False):
    """Extracts a given tarball to the destination directory"""
    tar_filepath = Path(tar_filename)
    if not tar_filepath.exists():
        raise FileNotFoundError(f"Cannot find the {tar_filepath}")
    try:
        with tarfile.open(tar_filepath, "r:gz") as tar_file:
            tar_file.extractall(dest_dir)
    except Exception as e:
        logging.error("Unable to extract %s to %s", tar_filepath, dest_dir)
        # Reraise the exception and don't continue!!
        raise e
    if keep_tarball:
        tar_filename.rename(dest_dir / tar_filename.name)
    else:
        tar_filepath.unlink()
