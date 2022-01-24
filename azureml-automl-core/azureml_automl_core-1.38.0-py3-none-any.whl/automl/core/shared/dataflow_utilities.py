# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for Dataflows."""

from typing import Any, Dict

import azureml.dataprep as dprep


class PicklableDataflow:
    """
    This class is a wrapper around a Dataflow that can be serialized to/from pickle.

    (The Dataflow object cannot be pickled directly -- it can throw an exception.)
    """

    def __init__(self, dataflow: dprep.Dataflow) -> None:
        """
        Initialize a PicklableDataflow.

        :param dataflow: The input Dataflow.
        """
        self.dataflow = dataflow

    def get_dataflow(self) -> dprep.Dataflow:
        """
        Return the inner Dataflow.

        :return: the inner Dataflow.
        """
        return self.dataflow

    def __getstate__(self) -> Dict[str, dprep.Dataflow]:
        """Get a dictionary representing the object's current state (used for pickling)."""
        return {'dataflow_json': self.dataflow.to_json()}

    def __setstate__(self,
                     newstate: Dict[str, dprep.Dataflow]) -> None:
        """Set the object's state based on a state dictionary (used for unpickling)."""
        self.dataflow = dprep.Dataflow.from_json(newstate['dataflow_json'])
