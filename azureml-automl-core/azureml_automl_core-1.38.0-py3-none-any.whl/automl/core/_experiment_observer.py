# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""

from typing import Any, Optional, TextIO
import enum
import os


class ExperimentStatus(enum.Enum):
    """Possible status codes for an Experiment."""

    DatasetEvaluation = 'DatasetEvaluation'
    FeaturesGeneration = 'FeaturesGeneration'
    DatasetCrossValidationSplit = 'DatasetCrossValidationSplit'
    DatasetFeaturization = 'DatasetFeaturization'
    DatasetBalancing = 'DatasetBalancing'
    AutosettingsSelected = 'ForecastingAutoSetting'
    DatasetFeaturizationCompleted = 'DatasetFeaturizationCompleted'
    TextDNNTraining = "TextDNNTraining"
    TextDNNTrainingProgress = "TextDNNTrainingProgress"
    TextDNNTrainingCompleted = "TextDNNTrainingCompleted"
    ModelSelection = 'ModelSelection'

    # Model Explanation related status
    BestRunExplainModel = 'BestRunExplainModel'
    PickSurrogateModel = 'PickSurrogateModel'
    ModelExplanationDataSetSetup = 'ModelExplanationDataSetSetup'
    EngineeredFeaturesExplanations = 'EngineeredFeatureExplanations'
    RawFeaturesExplanations = 'RawFeaturesExplanations'
    FailedModelExplanations = 'FailedModelExplanations'

    def __str__(self) -> str:
        """Return the value of the enumeration."""
        return str(self.value)


class ExperimentObserver:
    """Observer pattern implementation for the states of an AutoML Experiment."""

    def __init__(self, file_handler: Optional[TextIO]) -> None:
        """Initialize an instance of this class."""
        self.file_handler = file_handler

    def report_status(self, status: ExperimentStatus, description: str,
                      carriage_return: bool = False) -> None:
        """Report the current status for an experiment."""
        try:
            if self.file_handler is not None:
                esc_char = '\r' if carriage_return else os.linesep
                print("\rCurrent status: {}. {}".format(status, description),
                      file=self.file_handler,
                      end=esc_char)
        except Exception:
            print("Failed to report status.")


class NullExperimentObserver(ExperimentObserver):
    """Null pattern implementation for an ExperimentObserver."""

    def __init__(self, run_instance: Optional[Any] = None) -> None:
        """Instantiate a new instance of this class."""
        super(NullExperimentObserver, self).__init__(None)
        self.run_instance = run_instance

    def report_status(self, status: ExperimentStatus, description: str, carriage_return: bool = False) -> None:
        """Report the current status for an experiment. Does nothing in this implementation."""
        pass

    def report_progress(
        self,
        status: ExperimentStatus,
        progress: float,
        carriage_return: bool = False
    ) -> None:
        """Report the current progress for an experiment. Does nothing in this implementation"""
        pass
