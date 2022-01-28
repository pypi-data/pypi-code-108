"""Module grouping some data-classes and a parser for reading and parsing the
ExoMol master file *exomol.all*.
"""

import warnings
from pathlib import Path

from pyvalem.formula import Formula, FormulaParseError

from .exceptions import AllParseError, AllParseWarning, LineValueError, LineCommentError
from .utils import DataClass
from .utils import get_file_raw_text_over_api, parse_exomol_line


# noinspection PyUnresolvedReferences
class Molecule(DataClass):
    """A data class representing the molecule instance.

    All the parameters passed are stored as instance attributes.

    Parameters
    ----------
    names : list of str
    formula : str
    isotopologues : dict of Isotopologue
        The `Isotopologue` instances are stored under the keys of
        `Isotopologue.formula`.
    """

    def __init__(self, names, formula, isotopologues):
        super().__init__(names=names, formula=formula, isotopologues=isotopologues)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.formula})"


# noinspection PyUnresolvedReferences
class Isotopologue(DataClass):
    """A data class representing a molecule instance.

    All the parameters passed are stored as instance attributes.

    Parameters
    ----------
    inchi_kay : str
    iso_slug : str
    iso_formula : str
    dataset_name : str
    version : int
    """

    def __init__(self, inchi_key, iso_slug, iso_formula, dataset_name, version):
        super().__init__(
            inchi_key=inchi_key,
            iso_slug=iso_slug,
            iso_formula=iso_formula,
            dataset_name=dataset_name,
            version=version,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.iso_slug})"


class AllParser:
    """Class which handles parsing the *exomol.all* file.

    Parses the *.all* file specified by the `path` argument passed and leading to
    the *.all* file on the local file system. If the `path` is not given, the *.all*
    file is requested via the ExoMol public API.
    Instantiating the class only saves the `raw_text` attribute, which gets parsed
    with the `parse` method into all the available data structured.
    All the *relevant* attributes are listed in the **Attributes** section.

    Parameters
    ----------
    path : str or Path, optional
        Path to the *exomol.all* file. If not passed, the file is requested over
        the ExoMol public API.

    Attributes
    ----------
    raw_text : str
    file_name : str
    version : int
    molecules : dict of Molecule
        The `Molecule` instances are stored under the keys of `Molecule.formula`.

    Raises
    ------
    APIError
        If `path` not passed and the ExoMol API request call results in an unsuccessful
        response.

    Notes
    -----
    See the ExoMol file standard as defined in the ExoMol release paper [1]_.

    References
    ----------
    .. [1] Tennyson J, et al. The ExoMol database: molecular line lists for
       exoplanet and other hot atmospheres. J Mol Spectrosc 2016;327:73–94.
       doi: 10.1016/j.jms.2016.05.002

    Examples
    --------
    Instantiate the parser:
    >>> parser = AllParser(path="tests/resources/exomol_data/exomol.all")
    >>> parser.file_name
    'exomol.all'
    >>> parser.raw_text[: 13]  # first 13 characters of the text
    'EXOMOL.master'

    Parse the exomol.all text:
    >>> parser.parse(warn_on_comments=True)
    >>> parser.id
    'EXOMOL.master'
    >>> parser.version
    20210707
    >>> molecule_parsed = parser.molecules['CaH']
    >>> type(molecule_parsed)
    <class 'exomole.read_all.Molecule'>
    >>> molecule_parsed.names
    ['Calcium monohydride', 'Calcium(I) hydride']
    >>> isotopologue_parsed = molecule_parsed.isotopologues['(40Ca)(1H)']
    >>> isotopologue_parsed
    Isotopologue(40Ca-1H)
    >>> type(isotopologue_parsed)
    <class 'exomole.read_all.Isotopologue'>
    >>> isotopologue_parsed.dataset_name
    'Yadin'
    >>> isotopologue_parsed.iso_slug
    '40Ca-1H'
    """

    def __init__(self, path=None):
        self.raw_text = None
        self.file_name = None
        self._save_raw_text(path)
        # placeholders for all the attributes
        self.id = None
        self.version = None
        self.num_molecules = None
        self.num_isotopologues = None
        self.num_datasets = None
        self.molecules = None

    def _save_raw_text(self, path):
        """Save the raw text of a *.all* file as an instance attribute.

        The *.all* file is either read from the local file system, or requested over the
        ExoMol public API, if `path` argument not passed.

        Parameters
        ----------
        path : str or Path, optional
            Path leading to the *.all* file. If not supplied, the file is requested over
            the ExoMol public API.
        """
        if path is None:
            self.raw_text = get_file_raw_text_over_api("all")
            self.file_name = "exomol.all"
        else:
            with open(path, "r") as fp:
                self.raw_text = fp.read()
            self.file_name = Path(path).name

    def parse(self, warn_on_comments):
        """Parse the *.all* file text from the `raw_text` attribute.

        Populates all the instance attributes incrementally, util it hits the end of
        the file, or one of the exceptions is raised, signaling inconsistent *.all*
        file.

        Parameters
        ----------
        warn_on_comments : bool
            If ``True``, the comments behind the ``#`` symbol on each line are checked
            against some expected comments (hard-coded in the method) and the
            `LineWarning` is raised if they do not match.

        Raises
        -------
        AllParseError
            Raised if value on any line cannot be cast to the expected `type`, or if
            the parser runs out of lines. This error signals an inconsistent *.all*
            file. Also raised when any other inconsistencies are detected, such as
            formulas not supported by the `PyValem` package, etc.

        Warns
        -----
        AllParseWarning
            This warning is raised if `num_isotopologues` or `num_datasets`
            do not agree with the the actual numbers of isotopologues and datasets
            respectively, extracted from the file lines. Also raised if the *.all*
            file lists more than a single dataset for any given isotopologue.
        LineWarning
            Raised if `warns_on_comments` is ``True`` and if the comment on any line
            does not match the expected text hard-coded in this method.
        """
        lines = self.raw_text.split("\n")
        n_orig = len(lines)

        def parse_line(expected_comment, val_type=None):
            return parse_exomol_line(
                lines,
                n_orig,
                expected_comment=expected_comment,
                file_name=self.file_name,
                val_type=val_type,
                warn_on_comments=warn_on_comments,
            )

        # catch all the parse_line-originated errors and wrap them in the AllParseError:
        try:
            self.id = parse_line("ID")
            if self.id != "EXOMOL.master":
                raise AllParseError(f"Unexpected ID in {self.file_name}")
            self.version = parse_line("Version number with format YYYYMMDD", int)
            self.num_molecules = parse_line("Number of molecules in the database", int)
            self.num_isotopologues = parse_line(
                "Number of isotopologues in the database", int
            )
            self.num_datasets = parse_line("Number of datasets in the database", int)
            self.molecules = {}

            # Verify the numbers of isotopologues and datasets by keeping track:
            all_isotopologues = []
            all_datasets = []
            # Also keep track of all the molecules with more than one dataset in a
            # single isotopologue:
            molecules_with_duplicate_isotopologues = []

            # loop over molecules:
            for _ in range(self.num_molecules):
                mol_names = []

                num_names = parse_line("Number of molecule names listed", int)

                # loop over the molecule names:
                for __ in range(num_names):
                    mol_names.append(parse_line("Name of the molecule"))

                mol_formula = parse_line("Molecule chemical formula")
                try:
                    Formula(mol_formula)
                except FormulaParseError as e:
                    raise AllParseError(f"{str(e)} (raised in {self.file_name})")

                num_isotopologues = parse_line(
                    "Number of isotopologues considered", int
                )
                mol_isotopologues = {}

                # loop over the isotopologues:
                for __ in range(num_isotopologues):
                    iso_inchi_key = parse_line("Inchi key of isotopologue")
                    iso_slug = parse_line("Iso-slug")
                    iso_formula = parse_line("IsoFormula")
                    try:
                        Formula(iso_formula)
                    except FormulaParseError as e:
                        raise AllParseError(f"{str(e)} (raised in {self.file_name})")
                    iso_dataset_name = parse_line("Isotopologue dataset name")
                    iso_version = parse_line("Version number with format YYYYMMDD", int)

                    isotopologue = Isotopologue(
                        inchi_key=iso_inchi_key,
                        iso_slug=iso_slug,
                        iso_formula=iso_formula,
                        dataset_name=iso_dataset_name,
                        version=iso_version,
                    )

                    if iso_formula not in mol_isotopologues:
                        mol_isotopologues[iso_formula] = isotopologue
                    else:
                        warnings.warn(
                            f"{mol_formula} lists more than one dataset for "
                            f"isotopologue {iso_formula}. Ignoring {iso_dataset_name}",
                            AllParseWarning,
                        )
                        molecules_with_duplicate_isotopologues.append(mol_formula)

                    all_datasets.append(iso_dataset_name)
                    all_isotopologues.append(isotopologue)

                # molecule slug is not present in the exomol.all data!
                self.molecules[mol_formula] = Molecule(
                    names=mol_names,
                    formula=mol_formula,
                    isotopologues=mol_isotopologues,
                )
        except (LineValueError, LineCommentError) as e:
            raise AllParseError(str(e))

        if self.num_isotopologues != len(all_isotopologues):
            warnings.warn(
                f"Number of isotopologues stated ({self.num_isotopologues}) does not "
                f"match the actual number ({len(all_isotopologues)})!",
                AllParseWarning,
            )

        if self.num_datasets != len(set(all_datasets)):
            warnings.warn(
                f"Number of datasets stated ({self.num_datasets}) does not match the "
                f"actual number ({len(set(all_datasets))})!",
                AllParseWarning,
            )
