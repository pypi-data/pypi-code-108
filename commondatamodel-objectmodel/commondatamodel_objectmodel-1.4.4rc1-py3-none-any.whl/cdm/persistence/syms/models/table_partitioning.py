# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator 0.17.0.0
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class TablePartitioning(Model):
    """Table partitioning information.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param keys: Table partitioning keys.
    :type keys: list of str
    :ivar partition_function_type:  Default value: "value" .
    :vartype partition_function_type: str
    """ 

    _validation = {
        'keys': {'required': True},
        'partition_function_type': {'required': True, 'constant': True},
    }

    _attribute_map = {
        'keys': {'key': 'Keys', 'type': '[str]'},
        'partition_function_type': {'key': 'PartitionFunctionType', 'type': 'str'},
    }

    partition_function_type = "value"

    def __init__(self, keys):
        self.keys = keys
