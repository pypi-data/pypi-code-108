import unittest.util


class _AssertsMixin(unittest.TestCase):
    def assertInBetween(
        self,
        lower,
        upper,
        value,
        inclusive=True,
        lower_inclusive=None,
        upper_inclusive=None,
        msg=None,
    ):
        if lower_inclusive is None:
            lower_inclusive = inclusive

        if upper_inclusive is None:
            upper_inclusive = inclusive

        checks = []
        error_message = []

        if lower_inclusive:
            checks.append(lower <= value)
            error_message.extend([lower, "<=", value])
        else:
            checks.append(lower < value)
            error_message.extend([lower, "<", value])

        if upper_inclusive:
            checks.append(value <= upper)
            error_message.extend(["<=", upper])
        else:
            checks.append(value < upper)
            error_message.extend(["<", upper])

        if not all(checks):
            self.fail(
                self._formatMessage(
                    msg,
                    "Value didn't lie within bounds: "
                    + " ".join(str(part) for part in error_message),
                )
            )

    def assertIsEmpty(self, collection, msg=None):
        try:
            next(iter(collection))
            raise self.failureException(
                self._formatMessage(
                    msg,
                    "Collection was not empty {}".format(
                        unittest.util.safe_repr(collection)
                    ),
                )
            )
        except StopIteration:
            pass

    def assertIsNotEmpty(self, collection, msg=None):
        try:
            next(iter(collection))
        except StopIteration:
            raise self.failureException(
                self._formatMessage(
                    msg,
                    "Collection was empty {}".format(
                        unittest.util.safe_repr(collection)
                    ),
                )
            )
