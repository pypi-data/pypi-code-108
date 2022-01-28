"""Module grouping some data-classes and the parser for reading and parsing the
ExoMol *.def* files.
"""
import warnings
from pathlib import Path

from pyvalem.formula import Formula, FormulaParseError

from .exceptions import LineValueError, LineCommentError, LineWarning, DefParseError
from .utils import DataClass
from .utils import get_file_raw_text_over_api, parse_exomol_line


# noinspection PyUnresolvedReferences
class Isotope(DataClass):
    """A data class representing isotope instances.

    All the parameters passed are stored as instance attributes.

    Parameters
    ----------
    number : int
    element_symbol : str
    """

    def __init__(self, number, element_symbol):
        super().__init__(number=number, element_symbol=element_symbol)

    def __repr__(self):
        return f"Isotope({self.number}{self.element_symbol})"


class IrreducibleRepresentation(DataClass):
    """A data class representing instances of irreducible representations.

    All the parameters passed are stored as instance attributes.

    Parameters
    ----------
    ir_id : str
        ID of the *irreducible representation*
    label : str
    nuclear_spin_degeneracy : int
    """

    def __init__(self, ir_id, label, nuclear_spin_degeneracy):
        super().__init__(
            id=ir_id, label=label, nuclear_spin_degeneracy=nuclear_spin_degeneracy
        )


class QuantumCase(DataClass):
    """A data class representing the quantum case instances.

    All the parameters passed are stored as instance attributes.

    Parameters
    ----------
    label : str
    """

    def __init__(self, label):
        super().__init__(label=label)


# noinspection PyUnresolvedReferences
class Quantum(DataClass):
    """A data class representing the quanta instances.

    All the parameters passed are stored as instance attributes.

    Parameters
    ----------
    label : str
    q_format : str
        The quantum format as specified by the *.def* file
    description : str
    """

    def __init__(self, label, q_format, description):
        super().__init__(label=label, format=q_format, description=description)

    def __repr__(self):
        return f"Quantum({self.label})"


class DefParser:
    """Class handling parsing of any particular *.def* file.

    Parses the *.def* file specified either by the `path` argument passed and leading to
    the *.def* file on the local file system, or by the trio of `molecule_slug`,
    `isotopologue_slug` and `dataset_name` arguments, in which case the *.def* file
    is requested via the ExoMol public API.
    Instantiating the class only saves the `raw_text` attribute, which can be parsed
    with the `parse` method into all the available info. All the *relevant* attributes
    are listed in the **Attributes** section.

    Parameters
    ----------
    path : str or Path, optional
        The path leading to the *.def* file. If supplied, all the other arguments are
        simply ignored.
    molecule_slug : str, optional
        Only required, if the `path` argument is not passed.
    isotopologue_slug : str, optional
        Only required, if the `path` argument is not passed.
    dataset_name : str, optional
        Only required, if the `path` argument is not passed.

    Attributes
    ----------
    raw_text : str
    file_name : str
    version : int
    iso_formula : str
    iso_slug : str
    isotopes : list of Isotope
    lifetime_availability : bool
    lande_factor_availability : bool
    quanta : list of Quantum

    Raises
    ------
    APIError
        If `path` not passed and the ExoMol API request call results in an unsuccessful
        response.

    Notes
    -----
    See the ExoMol file standard as defined in the **ExoMol release paper** [1]_.

    References
    ----------
    .. [1] Tennyson J, et al. The ExoMol database: molecular line lists for
       exoplanet and other hot atmospheres. J Mol Spectrosc 2016;327:73–94.
       doi: 10.1016/j.jms.2016.05.002

    Examples
    --------
    Instantiate the parser:
    >>> parser = DefParser(
    ...     path="tests/resources/exomol_data/CaH/40Ca-1H/Yadin/40Ca-1H__Yadin.def"
    ... )
    >>> parser.file_name
    '40Ca-1H__Yadin.def'
    >>> parser.raw_text[:10]  # first 10 characters of the text
    'EXOMOL.def'

    Parse the .def file:
    >>> parser.parse(warn_on_comments=True)
    >>> parser.id
    'EXOMOL.def'
    >>> parser.iso_formula
    '(40Ca)(1H)'
    >>> parser.mass
    40.970416
    >>> parser.isotopes
    [Isotope(40Ca), Isotope(1H)]
    >>> quanta = parser.quanta
    >>> quanta
    [Quantum(par), Quantum(v), Quantum(N), Quantum(e/f)]
    >>> quanta[0].description
    "total parity: '+' or '-'"
    >>> parser.lifetime_availability, parser.lande_factor_availability
    (True, False)

    Additional methods on the parsed data:
    >>> parser.get_quanta_labels()
    ['par', 'v', 'N', 'e/f']
    >>> # with parser.lifetime_availability, we expect 9 columns in the .states file
    >>> parser.get_states_header()
    ['i', 'E', 'g_tot', 'J', 'tau', 'par', 'v', 'N', 'e/f']
    """

    def __init__(
        self,
        path=None,
        molecule_slug=None,
        isotopologue_slug=None,
        dataset_name=None,
    ):
        self.raw_text = None
        self.file_name = None
        self._save_raw_text(path, molecule_slug, isotopologue_slug, dataset_name)
        # placeholders to all the attributes
        self.id = None
        self.iso_formula = None
        self.iso_slug = None
        self.dataset_name = None
        self.version = None
        self.inchi_key = None
        self.isotopes = None
        self.mass = None
        self.symmetry_group = None
        self.irreducible_representations = None
        self.max_temp = None
        self.num_pressure_broadeners = None
        self.dipole_availability = None
        self.num_cross_sections = None
        self.num_k_coefficients = None
        self.lifetime_availability = None
        self.lande_factor_availability = None
        self.num_states = None
        self.quanta_cases = None
        self.quanta = None
        self.num_transitions = None
        self.num_trans_files = None
        self.max_wavenumber = None
        self.high_energy_complete = None

    def _save_raw_text(self, path, molecule_slug, isotopologue_slug, dataset_name):
        """Save the raw text of a *.def* file as an instance attribute

        The *.def* file is either read from the local file system, or requested over the
        ExoMol public API, based on the attributes values.

        Parameters
        ----------
        path : str or Path, optional
            Path leading to the *.def* file. If supplied, all the other arguments are
            ignored.
        molecule_slug : str, optional
            Ignored if `path` is passed.
        isotopologue_slug : str or None
            Ignored if `path` is passed.
        dataset_name : str, optional
            Ignored if `path` is passed.
        """
        if path is None:
            self.raw_text = get_file_raw_text_over_api(
                "def", molecule_slug, isotopologue_slug, dataset_name
            )
            self.file_name = f"{isotopologue_slug}__{dataset_name}.def"
        else:
            with open(path, "r") as fp:
                self.raw_text = fp.read()
            self.file_name = Path(path).name

    def parse(self, warn_on_comments):
        """Parse the *.def* file text from the `raw_text` attribute.

        Populates all the instance attributes incrementally, util it hits the end of
        the file, or one of the exceptions is raised, signaling inconsistent *.def*
        file.

        Parameters
        ----------
        warn_on_comments : bool
            If ``True``, the comments behind the ``#`` symbol on each line are checked
            against some expected comments (hard-coded in the method) and the
            `LineWarning` is raised if they do not match.

        Raises
        -------
        DefParseError
            Raised if value on any line cannot be cast to the expected ``type``, or if
            the parser runs out of lines. This error signals an inconsistent *.def*
            file. Also raised when any other inconsistencies are detected, such as
            formula not supported by the `PyValem` package, etc.

        Warns
        -----
        LineWarning
            Raised if `warns_on_comments` is ``True`` and if the comment on any line
            does not match the expected text hard-coded in this method.
            Also raised if any empty line is present in the .def file, or of the
            number of isotope sections does not match the number of atoms in the
            isotopologue.

        Warnings
        --------
        Currently the parser stops after the *High Energy Complete* line and does not
        parse the rest of the *.def* file, as the info beyond this point in the *.def*
        file was not needed for the data product application which served as my
        motivation to write this package.
        """
        lines = self.raw_text.split("\n")
        n_orig = len(lines)

        def parse_line(expected_comment, val_type=None, local_lines=lines):
            return parse_exomol_line(
                local_lines,
                n_orig,
                expected_comment=expected_comment,
                file_name=self.file_name,
                val_type=val_type,
                warn_on_comments=warn_on_comments,
            )

        # catch all the parse_line-originated errors and wrap them in a higher-level
        # error:
        try:
            self.id = parse_line("ID")
            if self.id != "EXOMOL.def":
                raise DefParseError(f"Unexpected ID in {self.file_name}")
            self.iso_formula = parse_line("IsoFormula")
            self.iso_slug = parse_line("Iso-slug")
            self.dataset_name = parse_line("Isotopologue dataset name")
            self.version = parse_line("Version number with format YYYYMMDD", int)
            self.inchi_key = parse_line("Inchi key of molecule")
            self.isotopes = []
            num_atoms = parse_line("Number of atoms", int)
            try:
                formula = Formula(self.iso_formula)
            except FormulaParseError as e:
                raise DefParseError(f"{str(e)} (raised in {self.file_name})")
            if formula.natoms != num_atoms:
                raise DefParseError(f"Incorrect number of atoms in {self.file_name}")
            # many (probably all) .def files for polyatomic datasets actually do not
            # list all isotopes, but rather only all *distinct* isotopes.from
            # I'll handle this with a Warning.
            num_distinct_atoms = len(formula.atoms)

            def add_isotope(num, el_symbol):
                try:
                    Formula(f"({num}{el_symbol})")
                except FormulaParseError as exc:
                    raise DefParseError(f"{str(exc)} (raised in {self.file_name})")
                isotope = Isotope(number=num, element_symbol=el_symbol)
                self.isotopes.append(isotope)

            i = 0
            for i in range(num_distinct_atoms):
                number = parse_line(f"Isotope number {i + 1}", int)
                element_symbol = parse_line(f"Element symbol {i + 1}")
                add_isotope(number, element_symbol)
            if num_distinct_atoms < num_atoms:
                num_additional_isotopes_expected = num_atoms - num_distinct_atoms
                lines_clone = lines.copy()
                try:
                    for j in range(i + 1, i + 1 + num_additional_isotopes_expected):
                        number = parse_line(
                            f"Isotope number {j + 1}", int, local_lines=lines_clone
                        )
                        element_symbol = parse_line(
                            f"Element symbol {j + 1}", local_lines=lines_clone
                        )
                        add_isotope(number, element_symbol)
                except (LineValueError, LineCommentError):
                    # This means that the .def file lists only distinct isotopes, not
                    # all isotopes, as it should. Handle with Warning and continue with
                    # the original lines
                    warnings.warn(
                        f"Incorrect number of isotopes listed in {self.file_name}",
                        LineWarning,
                    )
                else:
                    # This means that the try clause did not raise anything, meaning
                    # all the isotopes were listed in the .def file. Need to sync
                    # lines with the lines_clone:
                    for _ in range(2 * num_additional_isotopes_expected):
                        lines.pop(0)

            iso_mass_amu = float(
                parse_line("Isotopologue mass (Da) and (kg)").split()[0]
            )
            self.mass = iso_mass_amu
            if round(self.mass, 2) != round(formula.mass, 2):
                warnings.warn(
                    f"Incorrect isotopologue mass listed in {self.file_name}",
                    LineWarning,
                )
                self.mass = float(formula.mass)
            self.symmetry_group = parse_line("Symmetry group")
            self.irreducible_representations = []
            num_irreducible_representations = parse_line(
                "Number of irreducible representations", int
            )
            for _ in range(num_irreducible_representations):
                ir_id = parse_line("Irreducible representation ID", int)
                label = parse_line("Irreducible representation label")
                nuclear_spin_degeneracy = parse_line("Nuclear spin degeneracy", int)
                ir = IrreducibleRepresentation(
                    ir_id=ir_id,
                    label=label,
                    nuclear_spin_degeneracy=nuclear_spin_degeneracy,
                )
                self.irreducible_representations.append(ir)
            self.max_temp = parse_line("Maximum temperature of linelist", float)
            self.num_pressure_broadeners = parse_line(
                "No. of pressure broadeners available", int
            )
            self.dipole_availability = bool(
                parse_line("Dipole availability (1=yes, 0=no)", int)
            )
            self.num_cross_sections = parse_line(
                "No. of cross section files available", int
            )
            self.num_k_coefficients = parse_line(
                "No. of k-coefficient files available", int
            )
            self.lifetime_availability = bool(
                parse_line("Lifetime availability (1=yes, 0=no)", int)
            )
            self.lande_factor_availability = bool(
                parse_line("Lande g-factor availability (1=yes, 0=no)", int)
            )
            self.num_states = parse_line("No. of states in .states file", int)
            self.quanta_cases = []
            self.quanta = []
            num_quanta_cases = parse_line("No. of quanta cases", int)
            # TODO: It is not entirely clear if num_quanta and related blocks should
            #       be nested under a quanta case, or not.
            #       If they are, the data structures need to be changed, and the
            #       parser tweaked.
            for _ in range(num_quanta_cases):
                self.quanta_cases.append(
                    QuantumCase(label=parse_line("Quantum case label"))
                )
            num_quanta = parse_line("No. of quanta defined", int)
            for i in range(num_quanta):
                label = parse_line(f"Quantum label {i + 1}")
                q_format = parse_line(f"Format quantum label {i + 1}")
                description = parse_line(f"Description quantum label {i + 1}")
                quantum = Quantum(
                    label=label, q_format=q_format, description=description
                )
                self.quanta.append(quantum)
            self.num_transitions = parse_line("Total number of transitions", int)
            self.num_trans_files = parse_line("No. of transition files", int)
            self.max_wavenumber = parse_line("Maximum wavenumber (in cm-1)", float)
            self.high_energy_complete = parse_line(
                "Higher energy with complete set of transitions (in cm-1)", float
            )
            # This is where I finish now, it would be nice to sort out the rest of the
            # file one day!
        except (LineValueError, LineCommentError) as e:
            raise DefParseError(str(e))

    def get_quanta_labels(self):
        """Quanta labels for all the quanta extracted from the parsed *.def* file.

        The `parse` method must have been called first and finished without errors.

        Returns
        -------
        list of str
        """
        return [q.label for q in self.quanta]

    def get_states_header(self):
        """Get the header (column names) for the associated *.states* file

        The column names consist of the mandatory part, canonically named as
        ["i", "E", "g_tot", "J"], followed by optional columns "tau", "g_J" and by
        the quanta labels.

        Returns
        -------
        list of str
        """
        states_header = ["i", "E", "g_tot", "J"]
        if self.lifetime_availability:
            states_header.append("tau")
        if self.lande_factor_availability:
            states_header.append("g_J")
        states_header.extend(self.get_quanta_labels())
        return states_header
