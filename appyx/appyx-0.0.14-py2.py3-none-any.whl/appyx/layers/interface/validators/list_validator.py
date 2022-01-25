from appyx.layers.domain.validators.object_validator import ObjectValidator


class ListValidator(ObjectValidator):
    '''
    List validator that currently implements two kind of validations:
        - Validations to the list as a whole
        - Validations that apply to a single element of the list
    '''
    def __init__(self, list_validators=None, element_validators=None):
        self._list_validators = list_validators or []
        self._element_validators = element_validators or []

    def _validate_with_result(self, list_to_validate, result):
        # Run validators that apply to the list as a whole
        for validator in self._list_validators:
            validator.validate_with_result(list_to_validate, result)

        # Run validators that apply to each element of the list
        for validator in self._element_validators:
            self._validate_for_each_element_of_list(list_to_validate, validator, result)

        return result

    def _validate_for_each_element_of_list(self, list_to_validate, validator, result):
        for element in list_to_validate:
            validator.validate_with_result(element, result)
        return result