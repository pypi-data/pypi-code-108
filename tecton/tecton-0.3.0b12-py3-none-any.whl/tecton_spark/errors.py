from typing import List


class TectonValidationError(ValueError):
    """
    Exception that indicates a problem in validating user inputs against
    the data in the system. Typically recoverable by the user.
    """


class AccessError(ValueError):
    """
    Exception that indicates a problem in accessing raw data. Information about connecting to data sources can be found here:
    https://docs.tecton.ai/v2/setting-up-tecton/03-connecting-data-sources.html
    """


class TectonInternalError(RuntimeError):
    """
    Exception that indicates an unexpected error within Tecton.
    Can be persistent or transient. Recovery typically requires involving
    Tecton support.
    """


def INGEST_DF_MISSING_COLUMNS(columns: List[str]):
    return TectonValidationError(f"Missing columns in the DataFrame: {', '.join(columns)}")


def INGEST_COLUMN_TYPE_MISMATCH(column_name: str, expected_type: str, actual_type: str):
    return TectonValidationError(
        f"Column type mismatch for column '{column_name}', expected {expected_type}, got {actual_type}"
    )
