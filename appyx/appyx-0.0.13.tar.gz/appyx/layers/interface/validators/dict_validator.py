from appyx.layers.domain.validators.object_validator import ObjectValidator


class DictValidator(ObjectValidator):
    def _validate_with_result(self, an_object, result):
        raise NotImplementedError()

    def validate_has_exact_keys(self, dictionary, expected_keys, result):
        return self._assert_keys_defined(dictionary, expected_keys, result)

    def _assert_keys_defined(self, dictionary, expected_keys, result):
        for key in expected_keys:
            self._assert_key_defined(dictionary, key, result)
        expected_keys_size = len(expected_keys)
        dictionary_keys_size = len(dictionary.keys())
        if dictionary_keys_size != expected_keys_size:
            result.add_error(f"Dictionary expected to have {expected_keys_size} keys has {dictionary_keys_size} keys")
        return result

    def _assert_key_defined(self, dictionary, expected_key, result):
        if expected_key not in dictionary:
            result.add_error(f"Key {expected_key} missing from dictionary")
        return result

    def validate_key_defined(self, dictionary, expected_key, result, validators=None):
        validators = validators or []
        result = self._assert_key_defined(dictionary, expected_key, result)
        if result.has_errors():
            return result

        value = dictionary[expected_key]
        for validator in validators:
            validator.validate(value, result)

        return result

    def validate_keys_defined(self, dictionary, expected_keys, result, validators=None):
        return self.validate_has_at_least_keys(dictionary, expected_keys, result, validators)

    def validate_has_at_least_keys(self, dictionary, expected_keys, result, validators=None):
        validators = validators or []
        for expected_key in expected_keys:
            self.validate_key_defined(dictionary, expected_key, result, validators)

        return result

    def validate_values_with_result(self, dictionary, validators, result):
        values = dictionary.values()
        for value in values:
            for validator in validators:
                validator.validate_with_result(value, result)

        return result

    def validate_keys_with_result(self, dictionary, validators, result):
        keys = dictionary.keys()
        for key in keys:
            for validator in validators:
                validator.validate_with_result(key, result)

        return result

    def validate_keys_included_in(self, dictionary, valid_keys, result=None):
        result = self._defined_result(result)
        for key in dictionary:
            self.validate_key_in(key, valid_keys, result)
        return result

    def validate_key_in(self, key, valid_keys, result):
        return self._assert_key_in(key, valid_keys, result)

    def _assert_key_in(self, key, expected_keys, result):
        if key not in expected_keys:
            result.add_error(f"Key {key} is not included in {expected_keys}")
        return result
