# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base abstract operator converter."""
from abc import ABC, abstractmethod

from azureml.automl.core.shared.exceptions import OnnxConvertException


class _AbstractOperatorConverter(ABC):
    """Abstract base class for the operator converters."""

    # Operator alias used by the upper level code, a static base property.
    # Subclasses should override this value in there constructor.
    OPERATOR_ALIAS = '__InvalidAlias__'

    def get_alias(self):
        """
        Get the converter's alias.

        :return: The operator alias of instance of subclasses.
        """
        converter_tp = type(self)
        alias = self.OPERATOR_ALIAS
        # Check if the alias is valid or not.
        if alias == _AbstractOperatorConverter.OPERATOR_ALIAS:
            msg = 'Invalid Operator Alias "{0}" assigned in operator converter class {1}'
            raise OnnxConvertException(msg.format(alias, converter_tp),
                                       reference_code="_abstract_operator_converter."
                                                      "_AbstractOperatorConverter.get_alias")\
                .with_generic_msg(msg.format("[MASKED]", "[MASKED]"))
        return alias

    @abstractmethod
    def setup(self):
        """Abstract method for setting up the converter."""
        raise NotImplementedError
