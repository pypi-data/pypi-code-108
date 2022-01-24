def make_list(input):
    """
    Utility function to ensure input is a list even with single entry
    """
    if not isinstance(input, list):
        return [input]
    else:
        return input


class InstrumentParameter:
    """
    Base class for all types of instrument parameters

    Classes derived from InstrumentParameter can be included both in the
    McStas instrument and guide_bot optimization logic. They are also used in
    constraints of the optimization. A InstrumentParameterContainer is defined
    in instrument_parameter_container.py, and an instance of this is used to
    keep all parameters which will be used by both optimizer and McStas.
    """
    def __init__(self, name):
        """
        Base initialization of InstrumentParameter with parameter name

        The InstrumentParameter is initialized with a str for its name. A
        value is initialized as None, meaning it has not been set yet. The
        category can be set to identify the origin of the parameter.

        Parameters
        ----------

        name : str
            Name of the parameter
        """
        self.name = name
        self.value = None
        self.category = None

    def clear(self):
        """
        Clears the stored value in the InstrumentParameter object.
        """

        self.value = None
    
    def calculate(self):
        """
        A calculation method needs to be provided by the derived class.
        """
        pass

    def get_value(self):
        """
        A get value method needs to be provided by the derived class, and
        should return the value of the InstrumentParameter.
        """
        print("Calling base class get_value! Problem!")

    def set_category(self, category):
        """
        Sets category for parameter

        Parameters
        ----------

        category : str
            Category describing the origin of the parameter
        """
        self.category = category


class FreeInstrumentParameter(InstrumentParameter):
    """
    Description of a Free parameter to be optimized within bounds

    A FreeInstrumentParameter is initialized with a upper and lower bound,
    which can each be None, yet have to be set before the parameter is used
    for actual optimization.
    """
    def __init__(self, name, lower_bound, upper_bound):
        """
        Initialization of FreeInstrumentParameter with name and bounds

        A free parameter can be used by the optimizer module, and will be
        optimized within the range given by the bounds. It is added to the
        container class that descripes a set of parameters, ensuring they
        are defined in the McStas instrument and are optimized while
        satisfying the constraints.

        Parameters
        ----------

        name : str
            Name of the FreeInstrumentParameter

        lower_bound : float
            Lower bound of valid interval for the parameter

        upper_bound : float
            upper bound of valid interval for the parameter
        """

        super().__init__(name)

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
    
    def set_value(self, value):
        """
        Sets the value of the FreeInstrumentParameter (temporarily)

        Parameters
        ----------

        value : float
            Value for the free parameter for this optimization step
        """

        self.value = value
    
    def get_value(self):
        """
        Retrieves the stored value in the FreeInstrumentParameter

        Returns the value of the parameter used in this optimization step

        Returns
        -------

        value : float
            Value for the free parameter for this optimization step
        """

        return self.value

    def get_limits(self):
        """
        Returns a list with the lower and upper limit of allowed interval

        Returns
        -------

        list
            Lower bound and upper bound in list
        """
        return [self.lower_bound, self.upper_bound]
    
    def get_lower_bound(self):
        """
        Returns the lower limit of the allowed interval for this parameter

        Returns
        -------

        float
            Lower bound for allowed parameter interval
        """
        return self.lower_bound
        
    def get_upper_bound(self):
        """
        Returns the upper limit of the allowed interval for this parameter

        Returns
        -------

        float
            Upper bound for allowed parameter interval
        """
        return self.upper_bound

    def ready_for_optimization(self):
        """
        Returns True if both upper and lower bound have been set

        Returns
        -------

        bool
            Whether or not the FreeInstrumentParameter has well defined bounds

        """
        if self.lower_bound is not None and self.upper_bound is not None:
            if self.lower_bound > self.upper_bound:
                raise RuntimeError("Larger lower bound detected in " + self.name)

            return True
        else:
            return False

    def __eq__(self, other):
        """
        Override equals operator for FreeInstrumentParameter

        Returns
        -------

        bool
            True if two objects have same name and limits, False otherwise
        """

        if not isinstance(other, FreeInstrumentParameter):
            return False

        if not self.name == other.name:
            return False

        if not self.upper_bound == other.upper_bound:
            return False

        if not self.lower_bound == other.lower_bound:
            return False

        return True

    def __repr__(self):
        """
        Returns string descriping this FreeInstrumentParameter
        """

        string = "Free parameter:      "
        if self.category is None:
            string += " "*15
        else:
            string += self.category + " "*(15-len(self.category))
        string += str(self.name) + " "
        if self.value is None:
            string += "which was not set"
        else:
            string += "with value set to " + str(self.value)
        
        string += " [" + str(self.lower_bound) + ", "
        string += str(self.upper_bound) + "]"

        return string


class limit_function:
    """
    Stores a function for a dynamic limit with dependents and constants

    Stores a function that can depend on a number of Parameters and
    a number of constants.
    """
    def __init__(self, dependent_on, function, constants=[]):
        self.dependent_on = make_list(dependent_on)
        self.function = function
        self.constants = make_list(constants)

        self.value = None

    def calculate(self):

        dependent_values = []
        for dependent in self.dependent_on:
            dependent.calculate()

        for dependent in self.dependent_on:
            returned_value = dependent.get_value()
            if returned_value is None:
                # Unable to calculate this parameter
                #raise RuntimeError("Could not calculate limit, hung on '" + dependent.name + "'!")
                return

            dependent_values.append(returned_value)

        for constant in self.constants:
            dependent_values.append(constant)

        try:
            self.value = self.function(*dependent_values)
        except:
            self.value = self.function(dependent_values)
            if isinstance(self.value, list):
                self.value = self.value[0]

    def get_value(self):
        if self.value is None:
            self.calculate()

        return self.value


class Interval:
    def __init__(self, start, end):
        """
        Creates a description of an interval with start and end

        The end should be after the start, otherwise an error is thrown
        """
        self.start = start
        self.end = end

        if self.start > self.end:
            raise RuntimeError("Trying to construct interval with start larger than end!")

    def get_length(self):
        """
        Returns length of the interval
        """
        return self.end - self.start

    def cut_with_interval(self, cut):
        """
        Cuts the interval with another illegal interval

        Returns a list of legal intervals, length will be either 1 or 2
        """
        # Interval covers entire allowed interval, nothing left
        if cut.start <= self.start and cut.end >= self.end:
            return []

        # Interval cuts from start and shortens the interval
        if cut.start <= self.start < cut.end:
            return [Interval(cut.end, self.end)]

        # Interval cuts from end and shortens the interval
        if cut.start < self.end <= cut.end:
            return [Interval(self.start, cut.start)]

        # Interval cuts in the middle and cuts it into two
        if cut.start > self.start and cut.end < self.end:
            return [Interval(self.start, cut.start),
                    Interval(cut.end, self.end)]

        # The cut interval does not overlap with the original
        return [self]


class DynamicIllegalInterval:
    def __init__(self, dependent_on, lower_function, upper_function, constants=[]):
        """
        Creates a dynamic illegal interval that can depend on other variables

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        function_lower : func
            Function that takes inputs equal to dependent_on + constants, lower end

        function_upper : func
            Function that takes inputs equal to dependent_on + constants, upper end

        constants : list of values
            List of values that will be used as constants in the function
        """
        self.lower_dynamic_limit = limit_function(dependent_on, lower_function, constants)
        self.upper_dynamic_limit = limit_function(dependent_on, upper_function, constants)

    def calculate(self):
        """
        Calculates the limits of the interval
        """
        self.lower_dynamic_limit.calculate()
        self.upper_dynamic_limit.calculate()

    def get_current_interval(self):
        """
        Returns the interval given the current state of the dependent parameters
        """
        return Interval(self.lower_dynamic_limit.get_value(), self.upper_dynamic_limit.get_value())


class RelativeFreeInstrumentParameter(FreeInstrumentParameter):
    """
    A FreeParameter where range and interval can be dynamically adjusted

    A RelativeFreeParameter is chosen between two limits, the optimizer will
    see limits of 0 to 1, and static limits exist that set the range for the
    value, yet dynamic limits can also be taken into account. The dynamic
    limits can for example be earlier start positions that set an earliest
    start point. The dynamic limits are calculated from other parameters and
    compared to the static limits, and the most restrictive interval is used.
    It is possible to add illegal intervals within the main interval which
    wont be chosen by the optimizer, these can be dynamic as well.

    Any number of dynamic lower and upper limit functions can be added.
    """
    def __init__(self, name, static_lower, static_upper):
        """
        RelativeFreeInstrumentParameter is built on FreeInstrumentParameter

        Provides a parameter that can have dynamic limits depending on other
        parameters in the instrument.

        name: str
            Name of parameter

        static_lower: float
            Static lower limit

        static_upper: float
            Static upper limit
        """
        super().__init__(name, 0, 1)
        self.static_lower = static_lower
        self.static_upper = static_upper

        self.dynamic_lower = []
        self.dynamic_upper = []

        self.illegal_dynamic_intervals = []

        self.all_dependent_on = set()

    def get_lower_static_bound(self):
        return self.static_lower

    def get_upper_static_bound(self):
        return self.static_upper

    def dependencies_calculated(self, calculated):
        """
        Method that checks if all the dependencies are in calculated set

        Retruns: bool
        """

        for dependent in self.all_dependent_on:
            if dependent not in calculated:
                return False

        return True

    def add_lower_dynamic(self, dependent_on, function, constants=[]):
        """
        Lower limit that may depend on other parameters

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        function : func
            Function that takes inputs equal to dependent_on + constants

        constants : list of values
            List of values that will be used as constants in the function
        """
        for dependent in make_list(dependent_on):
            self.all_dependent_on.add(dependent.name)

        self.dynamic_lower.append(limit_function(dependent_on, function, constants))

    def add_upper_dynamic(self, dependent_on, function, constants=[]):
        """
        Upper limit that may depend on other parameters

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        function : func
            Function that takes inputs equal to dependent_on + constants

        constants : list of values
            List of values that will be used as constants in the function
        """
        for dependent in make_list(dependent_on):
            self.all_dependent_on.add(dependent.name)

        self.dynamic_upper.append(limit_function(dependent_on, function, constants))

    def add_dynamic_illegal_interval(self, dependent_on, function_lower, function_upper, constants=[]):
        """
        Dynamic illegal interval that can depend on other parameters

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        function_lower : func
            Function that takes inputs equal to dependent_on + constants, lower end

        function_upper : func
            Function that takes inputs equal to dependent_on + constants, upper end

        constants : list of values
            List of values that will be used as constants in the function
        """
        for dependent in make_list(dependent_on):
            if not isinstance(dependent_on, InstrumentParameter):
                print("Following object given as dependent_on is not supported:")
                print(dependent_on)
                raise RuntimeError("Given parameter is not an InstrumentParameter")

            self.all_dependent_on.add(dependent.name)

        # Set up a dynamic illegal interval with function for upper and lower limit
        dynamic_interval = DynamicIllegalInterval(dependent_on, function_lower, function_upper, constants)
        self.illegal_dynamic_intervals.append(dynamic_interval)

    def set_value(self, value):
        """
        Input value not equal to exit due to limits

        Calculated from limits that can be dynamic, these calculations
        are performed after free parameters are set by the optimizer.
        """

        lower_limit = self.static_lower
        dynamic_lower_limits = []
        for dynamic in self.dynamic_lower:
            dynamic.calculate()
            dynamic_lower_limits.append(dynamic.get_value())

        upper_limit = self.static_upper
        dynamic_upper_limits = []
        for dynamic in self.dynamic_upper:
            dynamic.calculate()
            dynamic_upper_limits.append(dynamic.get_value())

        lower_limit = max([lower_limit] + dynamic_lower_limits)
        upper_limit = min([upper_limit] + dynamic_upper_limits)

        # Calculate all the dynamic illegal intervals
        calculated_illegal_intervals = []
        for dynamic in self.illegal_dynamic_intervals:
            dynamic.calculate()
            calculated_illegal_intervals.append(dynamic.get_current_interval())

        allowed_intervals = [Interval(lower_limit, upper_limit)]

        # Cut up the allowed intervals with the cutting feature
        for illegal_interval in calculated_illegal_intervals:
            original_allowed_intervals = allowed_intervals
            new_allowed_intervals = []
            for allowed_interval in original_allowed_intervals:
                new_allowed_intervals += allowed_interval.cut_with_interval(illegal_interval)
            allowed_intervals = new_allowed_intervals

        # Calculate a uniformly chosen random value on the random intervals
        full_length = 0
        for allowed_interval in allowed_intervals:
            full_length += allowed_interval.get_length()

        r_value = value*full_length

        accumulated_length = 0
        previous_accumulated_length = 0
        for allowed_interval in allowed_intervals:
            accumulated_length += allowed_interval.get_length()
            if r_value <= accumulated_length:
                self.value = allowed_interval.start - previous_accumulated_length + r_value
                break
            previous_accumulated_length = accumulated_length

    def __repr__(self):
        """
        Returns string description of this FreeInstrumentParameter
        """

        string = "Relative parameter:  "
        if self.category is None:
            string += " " * 15
        else:
            string += self.category + " " * (15 - len(self.category))
        string += str(self.name) + " "
        if self.value is None:
            string += "which was not set"
        else:
            string += "with value set to " + str(self.value)

        string += " [" + str(self.static_lower) + ", "
        string += str(self.static_upper) + "]"

        string += " x=[" + str(self.lower_bound) + ", "
        string += str(self.upper_bound) + "]"

        if len(self.dynamic_lower) > 0:
            string += "\n   dynamic lower limits:"
        for dynamic in self.dynamic_lower:
            string += "\n       "
            for dependent in dynamic.dependent_on:
                string += dependent.name + " "

        if len(self.dynamic_upper) > 0:
            string += "\n   dynamic upper limits:"
        for dynamic in self.dynamic_upper:
            string += "\n       "
            for dependent in dynamic.dependent_on:
                string += dependent.name + " "

        if len(self.illegal_dynamic_intervals) > 0:
            string += "\n   dynamic illegal intervals:"
        for dynamic in self.illegal_dynamic_intervals:
            string += "\n      "
            for dependent in dynamic.lower_dynamic_limit.dependent_on:
                string += dependent.name + " "
            for dependent in dynamic.upper_dynamic_limit.dependent_on:
                string += dependent.name + " "

        return string


class FixedInstrumentParameter(InstrumentParameter):
    """
    Description of fixed parameter that still needs to be tracked

    Even though the FixedInstrumentParameter is not optimized, it is still
    important as it can be used in constraints and calculations to be
    performed both in python and the McStas instrument file for each step in
    the optimization.
    """
    def __init__(self, name, value):
        """
        Sets the name and value for a fixed parameter

        Initialization of a FixedInstrumentParameter requires a name and a
        value, that can not be changed.

        Parameters
        ----------

        name : str
            Name of the FixedInstrumentParameter

        value : float
            Value associated with the FixedInstrumentParameter
        """
        super().__init__(name)
        self.value = value

    def get_value(self):
        """
        Return the value stored in the FixedInstrumentParameter.
        """

        return self.value
    
    def clear(self):
        """
        Clear method is overridden to ensure the fixed value is not removed.
        """

        # Since the value is fixed, remove capability of clearing
        pass

    def __repr__(self):
        """
        Returns a string describing this fixed parameter
        """

        string = "Fixed parameter:     "
        if self.category is None:
            string += " " * 15
        else:
            string += self.category + " " * (15 - len(self.category))
        string += str(self.name) + " "
        string += " with value " + str(self.value)

        return string


class DependentInstrumentParameter(InstrumentParameter):
    """
    The DependentInstrumentParameter can be calculated from other InstrumentParameters

    This class describes parameters that depend on other parameters, and can
    be calculated with a provided function. The function can also include
    constant values. There is no limit to the number of other parameters or
    constants that the function can depend on, but the inputs has to be
    ordered such that the parameters preceed the constants.
    """
    def __init__(self, name, dependent_on, dependent_function, constants=[]):
        """
        Creates an InstrumentParameter that depends on other parameters

        A DependentInstrumentParameter is using a supplied function to
        evaluate its value at every step in an optimization before it is being
        supplied to the McStas instrument. It can depend on any number of
        other InstrumentParameters, and they don't have to be in a container
        together in order to function. A DependentInstrumentParameter is
        allowed to depend on other DependentInstrumentParameters. Constants
        can also be used in the function, these must just be something that
        has a value when optimization happens. The function needs to have a
        number of inputs corresponding to the total InstrumentParameters and
        constants given, and the order is all InstrumentParameters first, then
        all constants.

        Parameters
        ----------

        name : str
            Name of the FreeInstrumentParameter

        dependent_on : list of InstrumentParameters
            List of InstrumentParameter objects that this parameter depends on

        dependent_function : func
            Function that takes inputs equal to dependent_on + constants

        constants : list of values
            List of values that will be used as constants in the function
        """
        super().__init__(name)
    
        # todo: check dependent_on is a instrument_parameter
        self.dependent_on = make_list(dependent_on)
        
        self.constants = make_list(constants)
        
        # todo: check dependent_function is a function
        self.dependent_function = dependent_function

        self.value = None

        self.all_dependent_on = set()
        for dependent in self.dependent_on:
            self.all_dependent_on.add(dependent.name)

    def get_value(self):
        """
        Gets the value stored in the object, but does not calculate it

        Returns
        -------
        float
            Value stored in object

        """
        #if self.value is None:
        #    raise ValueError("Calculate dependent value before getting!")
    
        return self.value

    def calculate(self):
        """
        Attempts to calculate the value for the DependentInstrumentParameter

        This method is recursive in the sense that it attempts to calculate
        the value for all InstrumentParameters that this InstrumentParameter
        depends on. If some of them can not be calculated yet, the method
        will exit early. Since it will be attempted to calculate all
        DependentInstrumentParameters, at some point it will succeed and get
        all the value attributes updated.
        """
    
        if self.value is not None:
            return
    
        dependent_values = []
        for dependent in self.dependent_on:
            dependent.calculate()

        for dependent in self.dependent_on:
            returned_value = dependent.get_value()
            if returned_value is None:
                # Unable to calculate this parameter
                return
            
            dependent_values.append(returned_value)
            
        for constant in self.constants:
            dependent_values.append(constant)
        
        try:
            self.value = self.dependent_function(*dependent_values)
        except:
            self.value = self.dependent_function(dependent_values)
            if isinstance(self.value, list):
                self.value = self.value[0]

    def depends_on_free(self):
        """
        Check if this parameter depends on any free parameters

        Returns
        -------

        bool
            True if a FreeInstrumentParameter is in dependent, even recursively
        """
        for dependent in self.dependent_on:
            if isinstance(dependent, FreeInstrumentParameter):
                return True
            elif isinstance(dependent, DependentInstrumentParameter):
                if dependent.depends_on_free():
                    return True

        return False

    def __repr__(self):
        """
        Returns string describing this DependentInstrumentParameter

        Returns
        -------

        str
            String describing this DependentInstrumentParameter
        """
        string = "Dependent parameter: "
        if self.category is None:
            string += " " * 15
        else:
            string += self.category + " " * (15 - len(self.category))
        string += str(self.name) + " "
        if self.value is None:
            string += "which was not calculated"
        else:
            string += "with value set to " + str(self.value)
        string += "\n   dependent on: "
        for dependent in self.dependent_on:
            string += str(dependent.name) + " "

        return string
