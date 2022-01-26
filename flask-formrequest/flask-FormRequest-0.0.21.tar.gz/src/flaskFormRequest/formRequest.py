import abc

from .filters import strip_filter
from .validators import (
    NoneValueException,
    StopValidation,
    ValidationError
)


class FormRequest(abc.ABC):
    def __init__(self, request) -> None:
        self._data = {}
        self._errors = {}
        self._filters = [strip_filter]
        self._request = request
        self.load_data()
        self.apply_filters()

    @property
    def data(self):
        return self._data

    @property
    def errors(self):
        return self._errors

    @property
    def request(self):
        return self._request

    def load_data(self):
        json_data = self._request.json or {}
        get_post_data = self._request.values.to_dict()
        files_data = self._request.files.to_dict()

        self._data = {**json_data, **get_post_data, **files_data}

    def apply_filters(self):
        for k, v in self._data.items():
            for f in self._filters:
                v = f(v)
            self._data[k] = v

    @abc.abstractmethod
    def rules(self):
        pass

    def validate(self):
        rules = self.rules()
        for field, validators in rules.items():
            errors = []
            for validator in validators:
                try:
                    new_val = validator(self._data.get(field), field, self.data, self.request)
                    self._data[field] = new_val
                except StopValidation as err:
                    errors.append(str(err))
                    break
                except ValidationError as err:
                    errors.append(str(err))
                except NoneValueException:
                    break
            if len(errors) > 0:
                self.errors[field] = errors
        return not bool(self.errors)
