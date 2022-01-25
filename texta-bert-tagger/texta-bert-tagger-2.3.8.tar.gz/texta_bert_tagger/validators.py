from .config import Config
from random import randint, sample
import os

"""
Status codes

0 - OK

1 - Invalid input (data_sample not dict)
2 - Invalid input (data_sample keys (labels) are not ints or strings)
3 - Invalid input (data_sample values are not lists)
4 - Invalid input (data_sample valuelist does not contain strings)
5 - Invalid input (data_sample contains only one label)

6 - Model with specified ID does not exist

7 - Invalid training args (args do not exist)
8 - Invalid training arg types
9 - Model is not loaded.
"""

class InputError(Exception):
    def __init__(self, status_code, msg):
        super().__init__()
        self.status_code = status_code
        self.msg = msg


class ModelNotExistingError(Exception):
    def __init__(self, status_code, msg):
        super().__init__()
        self.status_code = status_code
        self.msg = msg


class ArgumentValidator:
    def __init__(self):
        self.allowed_args = Config().to_dict()
        self.allowed_arg_types = self._get_allowed_types()


    def _get_allowed_types(self):
        allowed_types = {}
        for key, val in list(self.allowed_args.items()):
            if key == "padding" or key == "truncation":
                allowed_types[key] = [type(True), type("foo")]

            else:
                allowed_types[key] = [type(val)]
        return allowed_types


    def _is_allowed_arg(self, argument):
        if argument in self.allowed_args:
            return True
        return False


    def _arg_type_valid(self, kw, value):
        if type(value) in self.allowed_arg_types[kw]:
            return True
        return False


    def validate_arguments(self, **kwargs):
        for kw, value in list(kwargs.items()):
            if not self._is_allowed_arg(kw):
                raise InputError(status_code=7, msg=f"Invalid argument: {kw}")
            elif not self._arg_type_valid(kw, value):
                raise InputError(status_code=8, msg=f"Invalid argument type ({type(value)}) for keyword {kw}. Correct type in: {self.allowed_arg_types}.")
        return True


    def validate(self, **kwargs):
        try:
            self.validate_arguments(**kwargs)
            status_code = 0
            msg = "OK"
        except Exception as e:
            status_code = e.status_code
            msg = e.msg
        return {"status_code": status_code, "msg": msg}


class ModelExistingValidator:
    def __init__(self):
        pass


    def validate_saved_model(self, path):
        if not os.path.exists(path):
            print(path)
            raise ModelNotExistingError(status_code=6, msg=f"No model detected with path {path}.")
        return True


    def validate(self, path):

        try:
            self.validate_saved_model(path)
            status_code = 0
            msg = "OK"
        except Exception as e:
            #print(e)
            status_code = e.status_code
            msg =  e.msg
        return {"status_code": status_code, "msg": msg}


class ModelLoadedValidator:
    def __init__(self):
        pass


    def validate_model_loaded(self, model):
        if not model:
            raise ModelNotExistingError(status_code=9, msg=f"No model detected. Model should be loaded or trained!")
        return True


    def validate(self, model):
        self.validate_model_loaded(model)
        return True


class InputValidator:
    def __init__(self, lazy_validation=True):
        self.lazy_validation = lazy_validation # check only one random element for validation, otherwise check all (slow)
        self.key_type = None
        self.value_type = None
        self.elem_type = None
        self.arg_validator = ArgumentValidator()


    def _is_dict(self, data_sample):
        if not isinstance(data_sample, dict):
            return False
        return True


    def _keys_type_string_or_int(self, data_sample):
        keys = list(data_sample.keys())
        if self.lazy_validation:
            random_key = sample(keys, 1)[0]
            keys = [random_key]
        for key in keys:
            if not isinstance(key, str) and not isinstance(key, int):
                self.key_type = type(key)
                return False
        return True


    def _values_type_list(self, data_sample):
        values = list(data_sample.values())
        if self.lazy_validation:
            random_value = sample(values, 1)[0]
            values = [random_value]
        for value in values:
            if not isinstance(value, list):
                self.value_type = type(value)
                return False
        return True


    def _value_list_contains_strings(self, data_sample):
        values = list(data_sample.values())
        if self.lazy_validation:
            random_value_list = sample(values, 1)[0]
            random_elem = sample(random_value_list, 1)[0]
            values = [[random_elem]]
        for value_list in values:
            for elem in value_list:
                if not isinstance(elem, str):
                    self.elem_type = type(elem)
                    return False
        return True


    def _contains_more_than_one_label(self, data_sample):
        if len(data_sample) < 2:
            return False
        return True


    def validate_data_sample(self, data_sample):
        if not self._is_dict(data_sample):
            raise InputError(status_code=1, msg=f"Invalid input format ({type(data_sample)}). Correct format is {type({})}.")

        elif not self._keys_type_string_or_int(data_sample):
            raise InputError(status_code=2, msg=f"Invalid input keys format ({self.key_type}). Correct format is {type('')} or {type(1)}.")

        elif not self._values_type_list(data_sample):
            raise InputError(status_code=3, msg=f"Invalid input values format ({self.value_type}). Correct format is {(type([]))}.")

        #elif not self._value_list_contains_strings(data_sample):
        #    raise InputError(status_code=4, msg=f"Invalid input values element format ({self.elem_type}). Correct format is {(type(''))}.")

        elif not self._contains_more_than_one_label(data_sample):
            raise InputError(status_code=5, msg=f"Input contains {len(data_sample)} unique labels. At least 2 needed.")

        return True


    def validate(self, data_sample, **kwargs):

        self.validate_data_sample(data_sample)
        self.arg_validator.validate_arguments(**kwargs)

        return True
