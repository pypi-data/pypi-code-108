"""
This module contains an abstract parent class, defining the some common default functions for factor template classes.
"""


from abc import ABC


class FactorTemplate(ABC):
    """
    A base class for factor templates.
    """

    def __init__(self, var_templates=None, conditioning_var_templates=None, conditional_var_templates=None):
        """
        The initializer.

        :param var_templates: The variable string templates (i.e: ['a_{i}', 'b{i}'])
        :type var_templates: str list
        :param conditioning_var_templates: The conditioning variable string templates (i.e: ['a_{i}', 'b{i}'])
        :param conditional_var_templates:  The conditional variable string templates (i.e: ['a_{i}', 'b{i}'])
        """
        self._var_templates = None
        self._conditioning_var_templates = None
        self._conditional_var_templates = None
        if (conditioning_var_templates is None) and (conditional_var_templates is None):
            self._var_templates = var_templates
        elif (conditioning_var_templates is None) or (conditional_var_templates is None):
            error_msg = (
                "neither or both of conditioning_var_templates and conditional_var_templates should be None"
            )
            raise ValueError(error_msg)
        else:
            self._conditioning_var_templates = conditioning_var_templates
            self._conditional_var_templates = conditional_var_templates

    def formattable(self, format_dict):
        """
        Check if the different variable templates sets are formattable by the given format_dict.

        :param format_dict: The dictionary used to format the variable templates.
        :return: The result of the check.
        :rtype: bool
        """
        # pylint: disable=expression-not-assigned
        try:
            if self._var_templates is not None:
                [vt.format(**format_dict) for vt in self._var_templates]
            else:
                [vt.format(**format_dict) for vt in self._conditioning_var_templates]
                [vt.format(**format_dict) for vt in self._conditional_var_templates]
            return True
        # pylint: enable=expression-not-assigned
        except KeyError:
            return False
