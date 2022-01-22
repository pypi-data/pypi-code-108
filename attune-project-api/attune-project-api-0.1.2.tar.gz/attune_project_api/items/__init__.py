from typing import Annotated


# Commonly used type annotations for TupleFields
from attune_project_api.TupleFieldValidators import NotFalsyValidator

NotZeroLenStr = Annotated[str, NotFalsyValidator()]


def loadStorageTuples():
    from . import parameter_tuple

    from .step_tuples import loadStorageStepTuples

    loadStorageStepTuples()

    from attune_project_api.items.file_archive_tuples import (
        loadStorageFileArchiveTuples,
    )

    loadStorageFileArchiveTuples()
