from appyx.layers.domain.result import Result


class ObjectValidator:
    """
    Models a validator for an object.
    Answers whether an object is valid or not.
    It can answer a simple boolean
    or a Result with more meaningful data about how and why an object is or isn't valid.

    validate is the method which answers a simple boolean.
    validate_with_result is a method that answers a Result explaining the validity.
    Both methods can be called with a Result as optional parameter
    Note: really? it makes sense for validate_with_result, but for validate?
    """

    def validate(self, an_object, result=None):
        """
        :type an_object: object
        :type result: Result
        :rtype: bool
        """
        result = self.validate_with_result(an_object, result)
        return result.is_successful()

    def validate_with_result(self, an_object, result=None):
        """
        :type an_object: object
        :type result: Result
        :rtype: Result
        """
        result = self._defined_result(result)

        return self._validate_with_result(an_object, result)

    def _defined_result(self, result=None):
        if result is None:
            result = Result()
        return result

    @classmethod
    def default_datetime_format(cls):
        """Return a format to represent the date and time in ISO 8601 format"""

        return "%Y-%m-%dT%H:%M:%S.%f"

    # --- private methods ---

    def _validate_with_result(self, an_object, result):
        raise NotImplementedError("Subclass responsibility")
