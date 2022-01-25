from appyx.layers.domain.errors import BaseErrorFactory


class Result:
    """This class models the result from the validate or execute of an Interaction or Operation

    It has an object, which is set by the interaction/operation. It is the product of the execution.
    Example:
        1) Adding a new user would result in the result of that operation to have the user in the result object
        2) Closing a poll may return an object containing the boolean indicating success or failure of the poll,
        and a list of positive voters and negative voters. All of these in a dictionary.
    It has errors, which contain a list of problems in a human readable way. It is empty if the execution was successful

    Note that objects that return a Result should not throw/raise exceptions.
    Because any errors should be contained and explained in the Result.
    """

    def __init__(self):
        self._errors = []
        # TODO: Add warnings
        self._object = None

    def get_object(self):
        return self._object

    def set_object(self, object_to_set):
        self._object = object_to_set

    def is_successful(self):
        return len(self._errors) == 0

    def errors(self):
        return self._errors

    def error_codes(self):
        return [error.code() for error in self._errors]

    def has_error_with_code(self, error_code):
        return error_code in self.error_codes()

    def has_at_least_one_error_with_codes(self, error_codes):
        return any([error_code for error_code in error_codes if error_code in self.error_codes()])

    def add_error(self, an_object):
        if type(an_object) is list:
            self.add_errors(an_object)
            return

        if type(an_object) is str:
            error = BaseErrorFactory().simple_error(an_object)
        elif isinstance(an_object, Exception):
            error = BaseErrorFactory().unexpected_error(an_object)
        else:
            error = an_object

        self._errors.append(error)

    def add_errors(self, errors):
        for error in errors:
            self.add_error(error)

    def add_errors_from(self, a_result):
        self.add_errors(a_result.errors())

    def has_errors(self):
        return not self.is_successful()

    def replace_error(self, old_error_code, new_error):
        self._errors = [new_error if error.code() == old_error_code else error for error in self._errors]

    # Convenience method
    def errors_as_string(self):
        return ', '.join([str(error) for error in self.errors()])

    def __str__(self):
        return f'Result ({self._object}) with errors {self._errors}'

    def add_warning(self, text):
        # TODO: warning support in Result
        pass

    def delete_repeated_errors(self):
        errors_set = set(self.errors())
        self._errors = list(errors_set)

    @classmethod
    def with_error(cls, error):
        result = cls()
        result.add_error(error)
        return result
