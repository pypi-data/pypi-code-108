# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from msrest.serialization import Model


class InnerErrorResponse(Model):
    """A nested structure of errors.

    :param code: The error code.
    :type code: str
    :param inner_error: A nested list of inner errors. When evaluating errors,
     clients MUST traverse through all of the nested "innerErrors" and choose
     the deepest one that they understand.
    :type inner_error: ~reinforcementlearning.models.InnerErrorResponse
    """

    _attribute_map = {
        'code': {'key': 'code', 'type': 'str'},
        'inner_error': {'key': 'innerError', 'type': 'InnerErrorResponse'},
    }

    def __init__(self, *, code: str = None, inner_error=None, **kwargs) -> None:
        super(InnerErrorResponse, self).__init__(**kwargs)
        self.code = code
        self.inner_error = inner_error
