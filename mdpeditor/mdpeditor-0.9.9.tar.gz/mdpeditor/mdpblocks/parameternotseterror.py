class ParameterNotSetError(KeyError):
    """ Custom exception to handle unset parameters.

        Enable collection of multiple missing parameters to avoid multiple
        runs to uncover missing parameters.
    """
    def __init__(self):
        self.message = ""
        self.have_been_added = False

    def add(self, offending_block, offending_parameter, reason):
        """ add to the collection of key errors

            offending_block : where the error occurred
            message : error message to give
            offending_parameter: the parameter that is not set or set wrongly
        """
        self.message += ("\n" + f"{offending_block} | {offending_parameter}" +
                         f": {reason}")
        self.have_been_added = True


class SomeParametersNotSetError(SystemExit):
    def __init__(self, errors):
        super().__init__("\n".join([error.message for error in errors]))
