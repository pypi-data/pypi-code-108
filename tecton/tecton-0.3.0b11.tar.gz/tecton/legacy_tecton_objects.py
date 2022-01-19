"""
All of these objects are deprecated in the new API.
This file will get cleaned up when we stop supporting FWV1 SDK versions on the server side.
"""
from tecton.tecton_errors import TectonValidationError


class DataSourceConfig:
    """
    DEPRECATED, please use Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError("'DataSourceConfig' class is deprecated.")


class VirtualDataSource:
    """
    DEPRECATED: please use 'BatchDataSource' or 'StreamDataSource' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError(
            "'VirtualDataSource' class is deprecated. Please use 'BatchDataSource' or 'StreamDataSource' instead."
        )


def sql_transformation(*args, **kwargs) -> None:
    """
    DEPRECATED: please use 'transformation' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """
    raise TectonValidationError("'sql_transformation' class is deprecated. Please use 'transformation' instead.")


def pyspark_transformation(*args, **kwargs) -> None:
    """
    DEPRECATED: please use 'transformation' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """
    raise TectonValidationError("'pyspark_transformation' class is deprecated. Please use 'transformation' instead.")


def online_transformation(*args, **kwargs) -> None:
    """
    DEPRECATED: please use 'transformation' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """
    raise TectonValidationError("'online_transformation' class is deprecated. Please use 'transformation' instead.")


class NewEMRClusterConfig:
    """
    DEPRECATED: please use 'EMRClusterConfig' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError("'NewEMRClusterConfig' class is deprecated. Please use 'EMRClusterConfig' instead.")


class NewDatabricksClusterConfig:
    """
    DEPRECATED: please use 'DatabricksClusterConfig' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError(
            "'NewDatabricksClusterConfig' class is deprecated. Please use 'DatabricksClusterConfig' instead."
        )


class MaterializationConfig:
    """
    DEPRECATED: please use Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError("'MaterializationConfig' class is deprecated.")


class TemporalAggregateFeaturePackage:
    """
    DEPRECATED: please use 'BatchWindowAggregateFeatureView' or 'StreamWindowAggregateFeatureView' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError(
            "'TemporalAggregateFeaturePackage' class is deprecated. Please use 'BatchWindowAggregateFeatureView' or 'StreamWindowAggregateFeatureView' instead."
        )


class TemporalFeaturePackage:
    """
    DEPRECATED: please use 'BatchFeatureView' or 'StreamFeatureView' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError(
            "'TemporalFeaturePackage' class is deprecated. Please use 'BatchFeatureView' or 'StreamFeatureView' instead."
        )


class OnlineFeaturePackage:
    """
    DEPRECATED: please use 'OnDemandFeatureView' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError(
            "'OnlineFeaturePackage' class is deprecated. Please use 'OnDemandFeatureView' instead."
        )


class PushFeaturePackage:
    """
    DEPRECATED: please use 'FeatureTable' from Tecton's V2 API: https://docs.tecton.ai/v2.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise TectonValidationError("'PushFeaturePackage' class is deprecated. Please use 'FeatureTable' instead.")
