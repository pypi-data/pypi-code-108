# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import torch

try:
    import horovod.torch as hvd
except ImportError:
    hvd = None

logger = logging.getLogger(__name__)


class DistributedHelper:
    """Helper for running a distributed job."""

    _rank = None

    @classmethod
    def initialize(cls):
        """Do the necessary initialization for a distributed job."""
        if hvd is None:
            logger.info('Horovod import failed.')
        else:
            logger.info('Horovod import succeeded')
            hvd.init()
            cls._rank = hvd.rank()
            if torch.cuda.is_available():
                torch.cuda.set_device(hvd.local_rank())

    @classmethod
    def is_master_node(cls) -> bool:
        """Return if the current node is the master node."""
        return hvd is None or cls._rank == 0
