from . import default

class JunosConfigReturnValues(default.ReturnValues):
    def pretty_diff(self):
        try:
            return self.data['diff']['prepared']
        except LookupError:
            return super().pretty_diff()

    def pretty_error(self):
        # NOTE: Currently this is the same as the default ReturnValues!
        return super().pretty_error()
