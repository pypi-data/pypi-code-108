# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from msrest.serialization import Model


class RunDetails(Model):
    """Contains the details of a run.

    All required parameters must be populated in order to send to Azure.

    :param run_id: Required. The identifier for a run.
    :type run_id: str
    :param target: Required. Target refers to compute where the job is
     scheduled for execution.
    :type target: str
    """

    _validation = {
        'run_id': {'required': True},
        'target': {'required': True},
    }

    _attribute_map = {
        'run_id': {'key': 'runId', 'type': 'str'},
        'target': {'key': 'target', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(RunDetails, self).__init__(**kwargs)
        self.run_id = kwargs.get('run_id', None)
        self.target = kwargs.get('target', None)
