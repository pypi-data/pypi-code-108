"""
Components of the Constant model. Contains names of database entries and Base class for an object that simplifies
accessing the database (tab completion, etc.)
"""
from enum import Enum
from typing import List

from dkist_processing_common._util.constants import ConstantsDb


class BudName(str, Enum):
    """
    Controlled list of names for constant stems (buds)
    """

    instrument = "INSTRUMENT"
    num_cs_steps = "NUM_CS_STEPS"
    num_modstates = "NUM_MODSTATES"
    proposal_id = "PROPOSAL_ID"
    average_cadence = "AVERAGE_CADENCE"
    maximum_cadence = "MAXIMUM_CADENCE"
    minimum_cadence = "MINIMUM_CADENCE"
    variance_cadence = "VARIANCE_CADENCE"
    num_dsps_repeats = "NUM_DSPS_REPEATS"
    spectral_line = "SPECTRAL_LINE"
    dark_exposure_times = "DARK_EXPOSURE_TIMES"


class ConstantsBase:
    """
    This class puts all constants (from the constant flowers flower pot) in a single property on task classes

    It also provides some default constants, but is intended to be subclassed by instruments.

    To subclass:

        1. Create the actual subclass. All you need to do is add more @properties for the constants you want

        2. Add/update the instrument's ScienceTask.__init__ function to look similar to this:

            -----
            def __init__(
                self,
                recipe_run_id: int,
                workflow_name: str,
                workflow_version: str,
            ):
                super().__init__(
                    recipe_run_id=recipe_run_id,
                    workflow_name=workflow_name,
                    workflow_version=workflow_version,
                )

                self.constants = ConstantsSubclass(self._constants_db)  #<------ This is the important line
            -----

            Note that the argument to the ConstantsSubclass will *always* be self._constants_db

    """

    def __init__(self, constants_db: ConstantsDb):
        self._db_dict = constants_db

    @property
    def proposal_id(self) -> str:
        return self._db_dict[BudName.proposal_id.value]

    @property
    def instrument(self) -> str:
        return self._db_dict[BudName.instrument.value]

    @property
    def average_cadence(self) -> float:
        return self._db_dict[BudName.average_cadence.value]

    @property
    def maximum_cadence(self) -> float:
        return self._db_dict[BudName.maximum_cadence.value]

    @property
    def minimum_cadence(self) -> float:
        return self._db_dict[BudName.minimum_cadence.value]

    @property
    def variance_cadence(self) -> float:
        return self._db_dict[BudName.variance_cadence.value]

    @property
    def num_dsps_repeats(self) -> int:
        return self._db_dict[BudName.num_dsps_repeats.value]

    @property
    def spectral_line(self) -> str:
        return self._db_dict[BudName.spectral_line.value]

    @property
    def dark_exposure_times(self) -> List[float]:
        return self._db_dict[BudName.dark_exposure_times.value]

    @property
    def stokes_params(self) -> [str]:
        return ["I", "Q", "U", "V"]
