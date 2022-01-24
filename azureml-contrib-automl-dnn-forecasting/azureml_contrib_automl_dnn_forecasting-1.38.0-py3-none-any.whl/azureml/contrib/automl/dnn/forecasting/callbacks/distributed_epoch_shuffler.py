# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callbacks which computes and uploads metric to run."""
import logging
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from forecast.callbacks import Callback
from torch.utils.data.distributed import DistributedSampler


logger = logging.getLogger(__name__)


class DistributedEpochShufflerCallback(Callback):
    """Wraps AutoML metric computation and upload in a callback."""

    def __init__(self):
        """Initialize callback to set_the epoch for shuffling."""
        super().__init__()
        self.sampler = None
        self.telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(interval=10)

    def set_sampler(self, sampler: DistributedSampler) -> None:
        """Set the sampler to set the epoch.

        :param sampler: Sampler to set the shuflle
        """
        self.sampler = sampler

    def on_train_epoch_begin(self, epoch: int) -> None:
        """Invoke prior to the beginning of an epoch in `model.fit()`."""
        # Sets the epoch for shuffling
        if self.sampler:
            self.sampler.set_epoch(epoch)
            logger.info(f"Set sampler epoch({epoch})")
        else:
            logger.info(f"No sampler to set epoch({epoch})")
