import logging
from typing import Any, Dict, List, Optional, Union

from aporia.core.http_client import HttpClient
from aporia.core.logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class FieldTrainingData:
    """Field training data."""

    def __init__(
        self,
        field_name: str,
        bins: Optional[List[Union[float, int, str, bool]]] = None,
        counts: Optional[List[int]] = None,
        min: Optional[float] = None,
        max: Optional[float] = None,
        sum: Optional[float] = None,
        median: Optional[float] = None,
        average: Optional[float] = None,
        std: Optional[float] = None,
        variance: Optional[float] = None,
        num_samples: Optional[int] = None,
        num_missing_values: Optional[int] = None,
        num_posinf_values: Optional[int] = None,
        num_neginf_values: Optional[int] = None,
        num_unique_values: Optional[int] = None,
        num_zero_values: Optional[int] = None,
    ):
        """Initializes a FieldTrainingData object.

        Args:
            field_name: Field name
            bins: Histogram bin edges.
            counts: Hitsogram.
            min: Minimum value.
            max: Maximum Value.
            sum: Sum of all values.
            median: Median values.
            average: Average value.
            std: Standard deviation value.
            variance: Variance value.
            num_samples: Number of data samples.
            num_missing_values: Number of missing values.
            num_posinf_values: Number of positive infinite values.
            num_neginf_values: Number of negative infinite values.
            num_unique_values: Number of unique values.
            num_zero_values: Number of zero values.
        """
        self.field_name = field_name
        self.bins = bins
        self.counts = counts
        self.min = min
        self.max = max
        self.sum = sum
        self.median = median
        self.average = average
        self.std = std
        self.variance = variance
        self.num_samples = num_samples
        self.num_missing_values = num_missing_values
        self.num_posinf_values = num_posinf_values
        self.num_neginf_values = num_neginf_values
        self.num_unique_values = num_unique_values
        self.num_zero_values = num_zero_values

    def serialize(self) -> dict:
        """Serializes the field training data to a dict.

        Returns:
            Serialized training data.
        """
        return {
            "fieldName": self.field_name,
            "bins": self.bins,
            "counts": self.counts,
            "min": self.min,
            "max": self.max,
            "sum": self.sum,
            "median": self.median,
            "average": self.average,
            "std": self.std,
            "variance": self.variance,
            "numSamples": self.num_samples,
            "numMissingValues": self.num_missing_values,
            "numPosinfValues": self.num_posinf_values,
            "numNeginfValues": self.num_neginf_values,
            "numUniqueValues": self.num_unique_values,
            "numZeroValues": self.num_zero_values,
        }


async def log_training_data(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    features: List[FieldTrainingData],
    labels: List[FieldTrainingData],
    raw_inputs: Optional[List[FieldTrainingData]] = None,
):
    """Reports training data.

    Args:
        http_client: Http client
        model_id: Model ID
        model_version: Mode version
        features: Training set features.
        labels: Training set labels.
        raw_inputs: Training set raw inputs.
    """
    query = """
        mutation LogTrainingSet(
            $modelId: String!,
            $modelVersion: String!,
            $features: [FieldTrainingData]!
            $labels: [FieldTrainingData]!
            $rawInputs: [FieldTrainingData]
        ) {
            logTrainingSet(
                modelId: $modelId,
                modelVersion: $modelVersion,
                features: $features
                labels: $labels
                rawInputs: $rawInputs
            ) {
                warnings
            }
        }
    """

    serialized_raw_inputs = None
    if raw_inputs is not None:
        serialized_raw_inputs = [field_data.serialize() for field_data in raw_inputs]

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "features": [field_data.serialize() for field_data in features],
        "labels": [field_data.serialize() for field_data in labels],
        "rawInputs": serialized_raw_inputs,
    }

    result = await http_client.graphql(query, variables)
    for warning in result["logTrainingSet"]["warnings"]:
        logger.warning(warning)


async def log_test_data(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    features: List[FieldTrainingData],
    predictions: List[FieldTrainingData],
    labels: List[FieldTrainingData],
    raw_inputs: Optional[List[FieldTrainingData]] = None,
):
    """Reports test data.

    Args:
        http_client: Http client
        model_id: Model ID
        model_version: Mode version
        features: Test set features.
        predictions: Test set features.
        labels: Test set labels.
        raw_inputs: Test set raw inputs.
    """
    query = """
        mutation LogTestSet(
            $modelId: String!,
            $modelVersion: String!,
            $features: [FieldTrainingData]!
            $predictions: [FieldTrainingData]!
            $labels: [FieldTrainingData]!
            $rawInputs: [FieldTrainingData]
        ) {
            logTestSet(
                modelId: $modelId,
                modelVersion: $modelVersion,
                features: $features
                predictions: $predictions
                labels: $labels
                rawInputs: $rawInputs
            ) {
                warnings
            }
        }
    """

    serialized_raw_inputs = None
    if raw_inputs is not None:
        serialized_raw_inputs = [field_data.serialize() for field_data in raw_inputs]

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "features": [field_data.serialize() for field_data in features],
        "predictions": [field_data.serialize() for field_data in predictions],
        "labels": [field_data.serialize() for field_data in labels],
        "rawInputs": serialized_raw_inputs,
    }

    result = await http_client.graphql(query, variables)
    for warning in result["logTestSet"]["warnings"]:
        logger.warning(warning)


async def log_training_sample_data(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    features: List[Dict[str, Any]],
    labels: List[Any],
):
    """Reports training sample.

    Args:
        http_client: Http client
        model_id: Model ID.
        model_version: Mode version.
        features: List of features.
        labels: List of labels.
    """
    await http_client.post(
        url=f"/models/{model_id}/versions/{model_version}/training_sample",
        data={"features": features, "labels": labels},
    )
