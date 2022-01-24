from guide_bot.parameters import instrument_parameters as ipars


class ElementGroup:
    """
    A collection of GuideElements with at most one free length

    ElementGroups are formed by adding an element at a time, where the
    properties of the group is then updated. Only the last element of the
    group may have a free length, the remaining must be fixed. A group
    contains information on the start_point and length of all included
    elements, and thus information on start_point can be propagated to the
    start of the ElementGroup.
    """

    def __init__(self):
        """
        Initialize ElementGroup, can't be with elements as these should be
        added one at a time with the add_element method.

        group_start is a equivalent to start_point for a group
        group_min/max_length is limits for total group length

        group_fixed_length is used to update the fixed length before the
        optional last free length GuideElement.

        The has_free attribute is set to True if an element with a free
        length is added to the group as the last element.
        """

        self.elements = []

        self.group_start = None
        self.group_min_start = None
        self.group_max_start = None

        self.group_min_length = None
        self.group_max_length = None

        self.group_fixed_length = 0.0

        self.has_free = False

    def add_element(self, element):
        """
        Adds Element to ElementGroup and updates attributes accordingly

        As each Element is added to the ElementGroup, the group properties are
        updated including description of possible start_point and length. The
        method does not support DependentInstrumentParameter as start_point or
        length input, this may be added later. Only the last Element of an
        ElementGroup can have a free length, an error is raised if a second
        Element with a free length is added.
        """

        #print("ElementGroup input:", element)

        # If no free length encountered yet, the fixed_length can be used to back project
        if isinstance(element.start_point, ipars.FixedInstrumentParameter):
            if self.group_start is not None:
                raise RuntimeError("Conflicting start points and lengths given! Overdetermined length problem.")

            self.group_start = element.start_point.get_value() - self.group_fixed_length

        elif isinstance(element.start_point, ipars.FreeInstrumentParameter):
            start_point = element.start_point
            if start_point.get_lower_bound() is not None:
                new_min_start = start_point.get_lower_bound() - self.group_fixed_length
                # if group_min_start exists already, check the new is more restrictive!
                if self.group_min_start is None:
                    self.group_min_start = new_min_start
                else:
                    self.group_min_start = max([self.group_min_start, new_min_start])

            if start_point.get_upper_bound() is not None:
                new_max_start = start_point.get_upper_bound() - self.group_fixed_length
                # if group_max_start exists already, check the new is more restrictive!
                if self.group_max_start is None:
                    self.group_max_start = new_max_start
                else:
                    self.group_min_start = min([self.group_max_start, new_max_start])  # old version had max here

        elif isinstance(element.start_point, ipars.DependentInstrumentParameter):
            raise RuntimeError("Not allowing start_point to be a DependentParameter.")
        else:
            raise RuntimeError("element.start_point was not any known parameter type!")

        if isinstance(element.length, ipars.FixedInstrumentParameter):
            self.group_fixed_length += element.length.get_value()
        elif isinstance(element.length, ipars.FreeInstrumentParameter):
            if self.has_free is True:
                raise ValueError("Can only have one free length in an ElementGroup!"
                                 + "Attempted to add a second.")

            self.has_free = True
            if element.length.get_lower_bound() is not None:
                self.group_min_length = self.group_fixed_length + element.length.get_lower_bound()
            if element.length.get_upper_bound() is not None:
                self.group_max_length = self.group_fixed_length + element.length.get_upper_bound()

        elif isinstance(element.length, ipars.DependentInstrumentParameter):
            raise RuntimeError("Not allowing length to be a DependentParameter.")
        else:
            raise RuntimeError("ERROR: Given element length is not a InstrumentParameter.")

        self.elements.append(element)

    def fix_start_in_last_group(self, total_length):
        """
        Fix start of the last ElementGroup as it has fixed length

        Since the last ElementGroup of a guide will include the gap between
        the guide and the sample which is always of fixed length, the last
        group will always lack a free length. Hence the start of the
        ElementGroup can be calculated and used directly. This method
        performs this correction, and should only be called for the last
        ElementGroup of a guide.
        """

        self.group_start = total_length - self.group_fixed_length

    def export_to_pars(self, instrument_parameters):
        """
        Exports change point parameters to instrument_parameters

        Each point where a guide element stops and the next begins is called
        a change point, and includes the source and sample. This is the way in
        which the instrument file is parametrized, and so these parameters are
        exported to the instrument_parameters so they can later be optimized.
        Some change points will be fixed, some free and some dependent on
        others due to a fixed length being used. Each ElementGroup is
        responsible for adding the change point before itself, but not after
        itself. The first can be free or fixed depending on user input, yet
        the subsequent will be dependent as all Elements but the last will
        have a fixed length.
        """

        if len(self.elements) == 0:
            return

        # Handle the first change point
        first_element = self.elements[0]
        cp_name = first_element.name + "_start_point"

        if self.group_start is not None:
            par = ipars.FixedInstrumentParameter(cp_name, self.group_start)
        else:
            par = ipars.FreeInstrumentParameter(cp_name, self.group_min_start, self.group_max_start)

        par.set_category(first_element.owner)
        print(first_element)
        print("First element in group, owner:", first_element.owner, " par category:", par.category)
        instrument_parameters.add_parameter(par)
        first_element.start_point_parameter = par

        if len(self.elements) == 1:
            return

        # Handle the internal change points
        previous_length = self.elements[0].length.get_value()
        for element in self.elements[1:]:
            # All subsequent starting points can be calculated from the previous

            cp_name = element.name + "_start_point"
            par = ipars.DependentInstrumentParameter(cp_name, par, lambda x, a: x + a, constants=previous_length)
            element.start_point_parameter = par

            par.set_category(element.owner)
            instrument_parameters.add_parameter(par)

            # In a group only the last element has a free length (None for element.length)
            # The last previous length will not be used
            if isinstance(element.length, ipars.FixedInstrumentParameter):
                previous_length = element.length.get_value()
            else:
                previous_length = None  # Ensures an error is raised if previous_length used regardless

    def __repr__(self):
        """
        Returns string describing an ElementGroup
        """
        string = "Group: \n"
        for element in self.elements:
            string += element.__repr__() + "\n"

        string += "group_start = " + str(self.group_start) + "\n"
        string += "group_min_start = " + str(self.group_min_start) + "\n"
        string += "group_max_start = " + str(self.group_max_start) + "\n"
        string += "group_min_length = " + str(self.group_min_length) + "\n"
        string += "group_max_length = " + str(self.group_max_length) + "\n"
        string += "group_fixed_length = " + str(self.group_fixed_length) + "\n"
        string += "has_free = " + str(self.has_free) + "\n"

        return string