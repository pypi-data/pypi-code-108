"""This module implements the class AcceptsMoistureMeasurement."""

from ml.fml40.features.properties.values.documents.reports.soil_moisture_measurement import (
    SoilMoistureMeasurement,
)
from ml.ml40.features.functionalities.functionality import Functionality


class AcceptsMoistureMeasurement(Functionality):
    """This functionality signalizes that SoilMoistureMeasurements can be
    processed."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def acceptMoistureMeasurement(self, input: SoilMoistureMeasurement):
        """Accepts the given SoilMoistureMeasurement."""
        pass
