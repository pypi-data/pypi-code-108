# -*- coding: utf-8 -*-
"""
    pip_services3_components.build.CreateException
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Create exception type
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.errors.InternalException import InternalException


class CreateException(InternalException):
    """
    Error raised when factory is not able to create requested component.
    """

    def __init__(self, correlation_id: Optional[str] = None, message_or_locator: str = None):
        """
        Creates an error instance and assigns its values.

        :param correlation_id: (optional) a unique transaction id to trace execution through call chain.

        :param message_or_locator: human-readable error or locator of the component that cannot be created.
        """
        super(CreateException, self).__init__(correlation_id, "CANNOT_CREATE", message_or_locator)
