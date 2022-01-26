from collections.abc import Iterable
from datetime import datetime
from enum import Enum
import logging
from typing import Set

from numpy import ndarray

from aporia.core.errors import AporiaError
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.utils import generate_features_schema_from_shape

logger = logging.getLogger(LOGGER_NAME)


class FragmentType(Enum):
    """Fragment types."""

    PREDICTION = "prediction"
    RAW_INPUTS = "raw_inputs"
    ACTUALS = "actuals"


class Fragment:
    """Inference fragment."""

    def __init__(self, type: FragmentType, data: dict):
        """Initializes a Fragment object.

        Args:
            type: Fragment type (this is mostly used for logging purposes)
            data: Fragment data
        """
        self.type = type
        self.data = data

    def serialize(self) -> dict:
        """Serializes the fragment.

        Returns:
            Serialized fragment
        """
        # Save the missing fields in a variable to avoid calculating set difference twice
        missing_fields = self.missing_fields
        if len(missing_fields) > 0:
            raise AporiaError("Missing required fields {}".format(missing_fields))

        return {"id": self.data["id"]}

    @property
    def required_fields(self) -> Set[str]:
        """Required fields property.

        Returns:
            Set of required field names.
        """
        return {"id"}

    @property
    def missing_fields(self) -> Set[str]:
        """Missing fields property.

        Returns:
            Set of missing field names
        """
        return self.required_fields - self.data.keys()

    def is_valid(self) -> bool:
        """Checks if the fragment is valid.

        Returns:
            True if the fragment is valid, false otherwise
        """
        if len(self.missing_fields) > 0:
            logger.warning("Invalid input - Missing required fields {}".format(self.missing_fields))
            return False

        if not isinstance(self.data["id"], str):
            logger.warning("Invalid input - id field must be a string.")
            return False

        return True


class PredictionFragment(Fragment):
    """Prediction fragment."""

    def __init__(self, data: dict, timestamp: datetime):
        """Initializes a PredictionFragment.

        Args:
            data: Prediction data
            timestamp: Current timestamp
        """
        super().__init__(type=FragmentType.PREDICTION, data=data)
        self.timestamp = timestamp

    def serialize(self) -> dict:
        """See base class."""
        serialized_fragment = super().serialize()
        serialized_fragment["predictions"] = self.data["predictions"]
        serialized_fragment["metrics"] = self.data.get("metrics")
        serialized_fragment["rawInputs"] = self.data.get("raw_inputs")
        serialized_fragment["actuals"] = self.data.get("actuals")

        if isinstance(self.data["features"], dict):
            serialized_fragment["features"] = self.data["features"]
        else:
            schema = generate_features_schema_from_shape(self.data["features"].shape)
            serialized_fragment["features"] = {
                name: value for name, value in zip(schema.keys(), self.data["features"].flat)
            }

        occurred_at = self.data.get("occurred_at")
        if occurred_at is None:
            occurred_at = self.timestamp

        serialized_fragment["occurredAt"] = occurred_at

        confidence = self.data.get("confidence")
        if confidence is not None and not isinstance(confidence, Iterable):
            confidence = [confidence]

        serialized_fragment["confidence"] = confidence

        return serialized_fragment

    @property
    def required_fields(self) -> Set[str]:
        """See base class."""
        return super().required_fields | {"features", "predictions"}

    def is_valid(self) -> bool:
        """See base class."""
        if not super().is_valid():
            return False

        features = self.data["features"]
        predictions = self.data["predictions"]
        metrics = self.data.get("metrics")
        occurred_at = self.data.get("occurred_at")
        confidence = self.data.get("confidence")
        raw_inputs = self.data.get("raw_inputs")
        actuals = self.data.get("actuals")

        if not (isinstance(features, (dict, ndarray)) and len(features) > 0):
            logger.warning("Invalid input - features must be a non-empty dict or ndarray")
            return False

        if not (isinstance(predictions, dict) and len(predictions) > 0):
            logger.warning("Invalid input - predictions must be a non-empty dict")
            return False

        if (metrics is not None) and not (isinstance(metrics, dict) and len(metrics) > 0):
            logger.warning("Invalid input - metrics must be a non-empty dict")
            return False

        if occurred_at is not None and not isinstance(occurred_at, (datetime, str)):
            logger.warning(
                "Invalid input - occurred_at must be a datetime object, or an ISO-8601 date string"
            )
            return False

        if confidence is not None and not isinstance(confidence, (float, Iterable)):
            logger.warning("Invalid input - confidence must be a float or a list of floats")
            return False

        if (raw_inputs is not None) and not (isinstance(raw_inputs, dict) and len(raw_inputs) > 0):
            logger.warning("Invalid input - raw_inputs must be a non-empty dict")
            return False

        if (actuals is not None) and not (isinstance(actuals, dict) and len(actuals) > 0):
            logger.warning("Invalid input - actuals must be a non-empty dict")
            return False

        return True


class RawInputsFragment(Fragment):
    """Raw inputs fragment."""

    def __init__(self, data: dict):
        """Initializes a RawInputsFragment.

        Args:
            data: Raw inputs data
        """
        super().__init__(type=FragmentType.RAW_INPUTS, data=data)

    def serialize(self) -> dict:
        """See base class."""
        serialized_fragment = super().serialize()
        serialized_fragment["rawInputs"] = self.data["raw_inputs"]

        return serialized_fragment

    @property
    def required_fields(self) -> Set[str]:
        """See base class."""
        return super().required_fields | {"raw_inputs"}

    def is_valid(self) -> bool:
        """See base class."""
        if not super().is_valid():
            return False

        if not (isinstance(self.data["raw_inputs"], dict) and len(self.data["raw_inputs"]) > 0):
            logger.warning("Invalid input - raw_inputs must be a non-empty dict")
            return False

        return True


class ActualsFragment(Fragment):
    """Prediction actuals fragment."""

    def __init__(self, data: dict):
        """Initializes a Actuals.

        Args:
            data: Actuals data
        """
        super().__init__(type=FragmentType.ACTUALS, data=data)

    def serialize(self) -> dict:
        """See base class."""
        serialized_fragment = super().serialize()
        serialized_fragment["actuals"] = self.data["actuals"]

        return serialized_fragment

    @property
    def required_fields(self) -> Set[str]:
        """See base class."""
        return super().required_fields | {"actuals"}

    def is_valid(self) -> bool:
        """See base class."""
        if not super().is_valid():
            return False

        if not (isinstance(self.data["actuals"], dict) and len(self.data["actuals"]) > 0):
            logger.warning("Invalid input - actuals must be a non-empty dict")
            return False

        return True
