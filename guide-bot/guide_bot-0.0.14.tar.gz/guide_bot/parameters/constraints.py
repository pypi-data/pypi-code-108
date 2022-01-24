from guide_bot.parameters.instrument_parameters import make_list


class Constraint:
    """
    Describes a constraint in the form of an inequality between Parameters

    A constraint is here defined as an function that can depend on Parameters
    and constants that is satisfied when the function returns a positive
    value. This is used under optimization to limit the search in some way,
    perhaps due to physical space constraints or just to enforce some
    relationship between parameters.
    """
    def __init__(self, dependent_on, function, constants=[]):
        """
        Creates a constraint which depends on InstrumentParameters and constants

        A constraint is initialized with a list of InstrumentParameters on
        which it depends, and a function that is to be evaluated. It can
        optionally have constants as well. The function need to take a number
        of input arguments corresponding to the total number of
        InstrumentParameters and constants used, with the InstrumentParameters
        before the constants in the function input. When the evaluated
        function returns a positive number, the constraint is considered
        satisfied.

        Parameters
        ----------

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        function : func
            Function that takes inputs equal to dependent_on + constants

        constants : list of values
            List of values that will be used as constants in the function
        """
        self.dependent_on = make_list(dependent_on)
        self.function = function
        self.constants = make_list(constants)

    def can_evaluate(self):
        """
        Method that checks whether the constraint can currently be evaluated

        A constraint can depend on FreeInstrumentParameters, which may not be
        set yet, and this method can be used to check if the constraint has
        the necessary information to be evaluated.
        """
        for dependent in self.dependent_on:
            if dependent.get_value() is None:
                return False

        return True

    def evaluate(self):
        """
        Evaluates constraint using the dependent InstrumentParameters and constants

        Evaluates the constraint function with the listed dependents and
        constants. Will raise an ValueError if not possible, one should check
        if the constraint can be evaluated first if there id doubt.

        Returns
        -------

        float
            Returns evaluated function, positive for satisfied constraint

        """
        for dependent in self.dependent_on:
            dependent.calculate()

        dependent_values = []
        for dependent in self.dependent_on:
            returned_value = dependent.get_value()
            if returned_value is None:
                raise ValueError("Need to calculate dependent parameters before evaluating constraint.")

            dependent_values.append(returned_value)

        for constant in self.constants:
            dependent_values.append(constant)

        try:
            return self.function(*dependent_values)
        except:
            return self.function(dependent_values)[0]

    def __repr__(self):
        """
        Returns string describing the constraint
        """
        if self.can_evaluate():
            value = self.evaluate()
            string = "Constraint with value: " + str(value) + ". Fulfilled: " + str(value > 0)
        else:
            string = "Constraint that can't yet be evaluated. "

        string += "\n   dependent on: "
        for dependent in self.dependent_on:
            string += str(dependent.name) + " "

        return string
