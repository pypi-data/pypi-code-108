"""
    PDF classes holding information about PDFs

    Example
    -------

    >>> from lhapdf_management.pdfsets import PDF
    >>> from lhapdf_management import environment
    >>> data_path = environment.datapath
    >>> pdf = PDF(data_path / "NNPDF31_nnlo_as_0118")
    >>> grids = pdf.get_member_grids(0)

"""
from pathlib import Path
from dataclasses import dataclass
from fnmatch import fnmatch
import numpy as np
import yaml


@dataclass
class SetInfo:
    """Stores PDF metadata: name, version, ID code."""

    name: str
    id_code: int
    version: int = None

    def match(self, pattern, exact=False):
        """Check whether the PDF matchs the given pattern (glob style)"""
        if exact:
            return self.name == pattern
        return fnmatch(self.name, pattern)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        """To be equal, two PDFs need to share only their name"""
        if hasattr(other, "name"):
            return other.name == self.name
        raise ValueError(f"Trying to compare a SetInfo object to {type(other)}:{other}")

    def load(self):
        """Try to load a PDF object, fails if the PDF does not exist in the system"""
        from lhapdf_management import environment

        # Import here to avoid circular imports
        pdf_path = environment.datapath / self.name
        return PDF(pdf_path, setinfo_object=self)

    def install(self):
        """Download and install the corresponding PDF"""
        from lhapdf_management import pdf_install

        # Import here to avoid circular imports
        pdf_install(self.name)


@dataclass
class GridPDF:
    """Stores a PDF grid data"""

    x: np.ndarray
    q2: np.ndarray
    flav: list
    grid: np.ndarray


def _load_data(pdf_file):
    """
    Reads pdf from file and retrieves a list of grids
    Each grid is a tuple containing numpy arrays (x,Q2, flavours, pdf)

    Note:
        the input q array in LHAPDF is just q, this functions
        squares the result and q^2 is used everwhere in the code

    Parameters
    ----------
        pdf_file: Path
            PDF .dat file

    Returns
    -------
        grids: list(GridPDF)
            list of GridPDFs containing all PDF information
    """
    pdf_file = Path(pdf_file)

    # We need to know how the grids are separated
    separator = "---"
    pdf_lines = pdf_file.read_text().split("\n")
    positions = [i for i, line in enumerate(pdf_lines) if line.strip() == separator]

    grids = []
    for separator_line in positions[:-1]:
        skip_me = separator_line + 1
        x = np.loadtxt(pdf_file, skiprows=skip_me, max_rows=1)
        q2 = pow(np.loadtxt(pdf_file, skiprows=skip_me + 1, max_rows=1), 2)
        flav = np.loadtxt(pdf_file, skiprows=skip_me + 2, max_rows=1)
        grid_size = len(x) * len(q2)
        grid = np.loadtxt(pdf_file, skiprows=skip_me + 3, max_rows=grid_size)
        grids.append(GridPDF(x, q2, flav, grid))

    return grids


class PDF:
    """Comodity object lazily-containing a LHAPDF PDF
    Receives a folder containing a PDF and stores the information
    to read it when necessary
    """

    _name = "None"

    def __init__(self, pdf_path, setinfo_object=None):
        # Ensure it is a path
        pdf_path = Path(pdf_path)
        # Perform some checks
        if not pdf_path.is_dir():
            raise ValueError(f"The given pdf path {pdf_path} is not a directory")
        self._name = pdf_path.name
        self._path = pdf_path
        self._info_file = pdf_path / f"{self._name}.info"
        self._info = None
        if not self._info_file.exists():
            raise FileNotFoundError(f"No info file found for {self._name}")
        # Check there is at least one dat file (is this true?)
        if not (pdf_path / f"{self._name}_0000.dat").exists():
            raise FileNotFoundError(f"No dat file found for {self._name}")
        # Store the metadata if given
        self._setinfo = setinfo_object
        self._grid = {}

    @property
    def name(self):
        return self._name

    @property
    def lhaID(self):
        if self._setinfo is None:
            return None
        return self._setinfo.id_code

    @property
    def info(self):
        """Information from the PDF .info file as a dictionary"""
        if self._info:
            return self._info
        with self._info_file.open() as info_file:
            self._info = yaml.safe_load(info_file)
        return self._info

    @property
    def description(self):
        """Description of the PDF as given in the .info file"""
        return self.info.get("SetDesc")

    @property
    def error_type(self):
        """Return the error type for the PDF"""
        return self.info.get("ErrorType")

    @property
    def version(self):
        """Return the version of the PDF that is installed"""
        return self.info.get("DataVersion")

    def get_member_grids(self, i):
        """Get a PDF member (as a list of GridPDF)"""
        i = str(i)
        member = self._grid.get(i)
        if member is not None:
            return member
        member_path = self._path / f"{self._name}_{i.zfill(4)}.dat"
        member = _load_data(member_path)
        self._grid[i] = member
        return member

    def get_all_member_grids(self):
        """Get all PDF members"""
        nm = self["NumMembers"]
        all_members = {i: self.get_member_grids(i) for i in range(nm)}
        return all_members

    def __getitem__(self, key):
        """Return an item from the info file"""
        item = self.info.get(key)
        if item is None:
            raise KeyError(f"key={key} not found in {self._name} info file")
        return item

    def __repr__(self):
        return self._name

    def __len__(self):
        return self.info["NumMembers"]


if __name__ == "__main__":
    pdf = PDF("/usr/share/lhapdf/LHAPDF/NNPDF31_nnlo_as_0118")
    grids = pdf.get_member_grids(0)
