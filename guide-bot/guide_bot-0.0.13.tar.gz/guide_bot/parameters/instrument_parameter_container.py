from guide_bot.parameters.instrument_parameters import InstrumentParameter
from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import RelativeFreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter
from guide_bot.parameters.constraints import Constraint

import random


class InstrumentParameterContainer:
    """
    Container for objects derived from InstrumentParameter

    The container class is used to pool all InstrumentParameters that will be
    used in the optimization process, facilitate the optimization process and
    export the necessary parameters to a McStas instrument to ensure they
    match. For optimizer iteration, a list of values for the free parameters
    is given to the container, which distributes the to the appropriate
    parameters, allowing all parameters to be calculated. The optimizer also
    needs lists of upper and lower bounds for the free parameters, which can
    be accessed from this class. It also allows exporting the parameters to
    a McStas file so that it is ensured the parameter names matches. When a
    InstrumentParameter is added, it is checked if it already exists, and if
    it does, it is ignored. This behavior is useful, as it avoid the same
    parameter getting two different values from the optimizer, and avoids
    declaration of two identical parameters in the McStas file, yet multiple
    components can still use the same parameter, effectively allowing the user
    to easily lock parameters together, for example start and end dimensions
    of a guide to keep it at a constant cross section. The container also
    keeps track of the constraints imposed on the InstrumentParameters, and
    provides a method for evaluating the constraints which is used by the
    optimizer.
    """
    def __init__(self):
        """
        Initializes an empty InstrumentParameterContainer

        The InstrumentParameterContainer holds parameters that will be used in
        the optimization and will be exported to the McStas instrument file.
        """

        self.free_parameters = []
        self.relative_parameters = []
        self.other_parameters = []
        self.all_parameters = []

        self.constraints = []

        self.current_category = None

    def get_N_free_parameters(self):
        """
        Returns the number of free parameters

        Returns

        int
            Number of free parameters
        """
        return len(self.free_parameters) + len(self.relative_parameters)

    def add_parameter(self, parameter):
        """
        Adds object derived from InstrumentParameter to the container

        Objects of type FreeInstrumentParameter, DependentInstrumentParameter
        and FixedInstrumentParameter are allowed. Duplicates are ignored.

        Parameters
        ----------

        parameter : InstrumentParameter
            Parameter that should be added to the container
        """
        if not isinstance(parameter, InstrumentParameter):
            raise ValueError("Attempted to add parameter, but it didn't "
                             + "inherit from InstrumentParameter.")

        if self.current_category is not None and parameter.category is None:
            parameter.set_category(self.current_category)

        if parameter in self.all_parameters:
            # Parameters are only allowed once in the container
            return

        if parameter.name in [par.name for par in self.all_parameters]:
            raise RuntimeError("Two instrument parameters with the same name added! Name:" + parameter.name)

        if isinstance(parameter, RelativeFreeInstrumentParameter):
            self.relative_parameters.append(parameter)
        elif isinstance(parameter, FreeInstrumentParameter):
            self.free_parameters.append(parameter)
        else:
            self.other_parameters.append(parameter)

        self.all_parameters.append(parameter)

    def add_new_parameter(self, *args, dependent_on=[], func=None, constants=[]):
        """
        Creates and adds a new parameter to the container, type depends on input

        This method will create a new InstrumentParameter of one of three
        types depending on the input format. All need a name as the first
        argument, and if just one additional value is given, it will become
        a FixedInstrumentParameter. Are two given, it will be a
        FreeInstrumentParameter with the specified limits. To create a
        DependentInstrumentParameter, one needs to use the keyword arguments
        dependent_on, func and optionally constants.

        Parameters (for FixedInstrumentParameter)
        -----------------------------------------

        first arg : str
            Name of the parameter

        second arg : float
            Fixed value for the Parameter


        Parameters (for FixedInstrumentParameter)
        -----------------------------------------

        first arg : str
            Name of the parameter

        second arg : float
            Lower bound for free parameter to be optimized

        third arg : float
            Lower bound for free parameter to be optimized


        Parameters (for DependentInstrumentParameter)
        ---------------------------------------------

        first arg : str
            Name of the parameter

        keyword arguments (required for Dependent)
        ------------------------------------------

        dependent_on : list
            List of InstrumentParameter objects on which this parameter depend

        func : function
            Function to evaluate, inputs from dependent_on first, then constants

        constants : list (optional)
            List of variables that can be evaluated, will be fed into the function

        """
        if len(dependent_on) != 0 and func is not None:
            par = DependentInstrumentParameter(args[0], dependent_on=dependent_on,
                                               func=func, constants=constants)
        elif len(args) == 2:
            par = FixedInstrumentParameter(args[0], args[1])
        elif len(args) == 3:
            par = FreeInstrumentParameter(args[0], args[1], args[2])

        self.add_parameter(par)

    def clear(self):
        """
        Clears all parameters in container, done between optimizer iterations
        """
        for par in self.all_parameters:
            par.clear()

    def get_lower_bounds(self):
        """
        Returns list with lower bounds for all free parameters
        """
        lbs = []
        for par in self.free_parameters:
            lbs.append(par.lower_bound)

        for par in self.relative_parameters:
            lbs.append(par.lower_bound)

        return lbs

    def get_upper_bounds(self):
        """
        Returns list with upper bounds for all free parameters
        """
        ubs = []
        for par in self.free_parameters:
            ubs.append(par.upper_bound)

        for par in self.relative_parameters:
            ubs.append(par.upper_bound)

        return ubs

    def set_current_category(self, category):
        """
        Sets the current category, which will be applied to all new parameters

        All parameters added subsequently will have this category attached to
        them. Can be set to None to disable.

        Parameters
        ----------

        category : str
            String describing the current category used to identify origin

        """

        self.current_category = category

    def set_values(self, optimizer_x):
        """
        Sets value of all free parameters based on state selected by optimizer

        The optimizer provides the new values for all free parameters in the
        next optimization step, and this function distributes them to the
        appropriate FreeInstrumentParameters, after which all the
        DependentInstrumentParameters are evaluated.

        Parameters
        ----------

        optimizer_x : list of length matching number of free parameters
            Values for each free parameter in list form
        """
        if len(self.free_parameters) + len(self.relative_parameters) != len(optimizer_x):
            raise ValueError("Mismatch between number of free parameters"
                             + " and length of given state!")

        calculated = set()

        input_for_free_parameters = optimizer_x[0:len(self.free_parameters)]
        for par, given_value in zip(self.free_parameters, input_for_free_parameters):
            par.set_value(given_value)
            calculated.add(par.name)

        # This assumes other parameters does not depend on relative parameters.
        for par in self.other_parameters:
            par.calculate()
            calculated.add(par.name)

        # need to set all before calculation
        input_for_relative_parameters = optimizer_x[len(self.free_parameters):]

        calculate_list = list(zip(self.relative_parameters, input_for_relative_parameters))

        limit = 10
        still_to_be_calculated = []
        while len(calculate_list):
            limit -= 1
            for par, given_value in calculate_list:
                # Check all dependencies already set
                if par.dependencies_calculated(calculated):
                    par.set_value(given_value)
                    calculated.add(par.name)
                else:
                    still_to_be_calculated.append((par, given_value))

            calculate_list = still_to_be_calculated
            random.shuffle(calculate_list)
            still_to_be_calculated = []

            if limit < 0:
                raise RuntimeError("Was not able to set all parameters! Is there a circular dependency?")

    def extract_instrument_parameters(self, optimizer_x=None):
        """
        From optimizer state returns dictionary with parameter : value pairs

        The optimizer state is given as a list with values for all free
        parameters, which is the distributed to the FreeInstrumentParameters
        within the container using the set_values method. Next a dictionary
        with all parameters and their evaluated values is returned, which can
        be used for input in the McStas instrument. If no state is given,
        the internal state of the container object is used.

        Parameters
        ----------

        optimizer_x : list of length matching number of free parameters
            Values for each free parameter in list form
        """

        if optimizer_x is not None:
            self.clear()
            self.set_values(optimizer_x)

        instrument_parameters = {}
        for par in self.all_parameters:
            instrument_parameters[par.name] = par.get_value()

        return instrument_parameters

    def add_constraint(self, constraint):
        """
        Add a Constraint object to the InstrumentParameterContainer

        Parameters
        ----------

        constraint : Constraint
            Adds a constraint of the type Constraint to the container
        """
        self.constraints.append(constraint)

    def add_new_constraint(self, dependent_on, function, constants=[]):
        """
        Creates a Constraint object and adds it to InstrumentParameterContainer

        Parameters
        ----------

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        function : func
            Function that takes inputs equal to dependent_on + constants

        constants : list of values
            List of values that will be used as constants in the function
        """
        self.constraints.append(Constraint(dependent_on, function, constants=constants))

    def evaluate_constraints(self, optimizer_x=None):
        """
        Evaluates the constraints stored in this object

        This methods evaluates all the constraints in the
        InstrumentParameterContainer, either using the current values saved
        or a new optimizer state provided by the user. Returns a list of
        values, one for each constraint, positive means satisfied constraint.

        Parameters
        ----------

        optimizer_x : list of length matching number of free parameters
            Values for each free parameter in list form

        Returns
        -------

        list of floats
            Status for each constraint, positive means satisfied
        """
        if optimizer_x is not None:
            self.set_values(optimizer_x)

        return_list = []
        for constraint in self.constraints:
            return_list.append(constraint.evaluate())

        return return_list

    def include_other_container(self, container):
        """
        Add information from another container to this container

        All parameters and constraints from another container can be included
        in this container, but is not copied. Duplicates are not transfered.

        Parameters
        ----------

        container : InstrumentParameterContainer
            Container from which all parameters and constraints are taken
        """
        for par in container.all_parameters:
            self.add_parameter(par)

        for constraint in container.constraints:
            self.add_constraint(constraint)

    def export_to_instrument(self, instrument):
        """
        Exports the parameters in the container to a McStasScript instrument

        This method adds each parameter in the container to the instrument
        as input parameters, and those that have a fixed value get a default
        value as well.
        """
        #for par in self.all_parameters:
        #    print(par)
        for par in self.all_parameters:
            if isinstance(par, FixedInstrumentParameter):
                value = par.get_value()
                instrument.add_parameter("double", par.name, value=value)
            else:
                instrument.add_parameter("double", par.name)

    def matching_free_parameters(self, other_container):
        """
        Checks if free parameters are identical for this and another container

        Parameters
        ----------

        other_container : InstrumentParameterContainer
            The InstrumentParameterContainer with parameters and constraints

        Returns
        -------

        bool
            True if parameters match, False otherwise
        """

        for self_par, other_par in zip(self.free_parameters, other_container.free_parameters):
            if not self_par == other_par:
                return False

        return True

    def fix_free_parameters(self, other_container, exclude=None):
        """
        Fix free / relative parameters in this container using values from other_container

        Will replace free parameters in this container with fixed parameters
        for each free parameter in the other container. This assumes the
        other container has its values set to an optimized state. It can be
        chosen to exclude a certain category of parameters to be read, this is
        used for avoiding overwriting for example the moderator parameters.

        Parameters
        ----------

        other_container : InstrumentParameterContainer
            The InstrumentParameterContainer with parameters and constraints

        Keyword arguments
        -----------------

        exclude : str
           Category of which parameters should be excluded for fixing
        """
        for free_par in other_container.free_parameters + other_container.relative_parameters:
            if exclude is not None and exclude == free_par.category:
                continue

            if free_par in self.free_parameters + self.relative_parameters:
                # remove parameter here
                self.all_parameters.remove(free_par)
                if free_par in self.free_parameters:
                    self.free_parameters.remove(free_par)
                if free_par in self.relative_parameters:
                    self.relative_parameters.remove(free_par)

                # create fixed parameter
                replacement_par = FixedInstrumentParameter(free_par.name, free_par.get_value())
                replacement_par.set_category(free_par.category)

                self.add_parameter(replacement_par)

                # Reassign dependent variables to the new fixed parameter
                for par in self.other_parameters:
                    if isinstance(par, DependentInstrumentParameter):
                        if free_par in par.dependent_on:
                            index = par.dependent_on.index(free_par)
                            par.dependent_on[index] = replacement_par

                # Reassign dependent variables in dynamic limits to the new fixed parameter
                for par in self.relative_parameters:
                    for dynamic in par.dynamic_lower + par.dynamic_upper:
                        if free_par in dynamic.dependent_on:
                            index = dynamic.dependent_on.index(free_par)
                            dynamic.dependent_on[index] = replacement_par

    def __repr__(self):
        """
        Method that returns string describing the InstrumentParameterContainer
        """
        string = ""
        for par in self.all_parameters:
            string += par.__repr__() + "\n"

        for constraint in self.constraints:
            string += constraint.__repr__() + "\n"

        return string
