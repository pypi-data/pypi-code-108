from guide_bot.base_elements import guide_elements
from guide_bot.base_elements import element_group as groups
from guide_bot.parameters import instrument_parameters as ipars

def length_system(elements, total_length, instrument_parameters):
    """
    System for handling length of each element with given constraints

    A total length from source to sample is given, along with a number of
    elements, each with their own constraints on starting distance from the
    source and length of the element. Some constraints are in the form of a
    fixed starting point or a fixed length, others as a range of allowed
    values. This function takes these constraints into account and adds a
    lower number of free parameters to the instrument_parameter container,
    describing the problem in terms of change points between each element.
    Some of these change points are in absolute distance from the source,
    while others are unitless parameters between 0 and 1 whos range depends
    on earlier parameters. This design avoids using constraints, as using
    too many of these makes it difficult for the optimizer to find legal
    parameter sets. The function is not yet able to clearly identify when
    an impossible problem is given.

    Parameters
    ----------

    elements : list of Element objects
        The elements describing this guide

    total_length : float
        The distance from source to sample along the guide

    instrument_parameters : InstrumentParameterContainer
        Parameter container where parameters can be added for optimization
    """

    # expect a list of elements, if not make it one
    if not isinstance(elements, list):
        elements = [elements]

    # Add the change point for guide to sample at the end at the sample location
    par = ipars.FixedInstrumentParameter("sample_cp", total_length)
    par.set_category("length_system")
    instrument_parameters.add_parameter(par)
    elements[-1].next_start_point_parameter = par  # last element told sample pos

    # Use fixed lengths to find additional fixed points which simplifies the problem
    propagate_fixed_lengths_to_start_points(elements, total_length)

    # Split into sections that each have a fixed start and end point.
    sections = []
    section = GuideSection()
    section.add_element(elements[0])
    section.set_start_point(0.0)

    for index in range(1, len(elements)):
        element = elements[index]
        if is_fixed_parameter(element.start_point):
            # end the current section
            fixed_point = element.start_point.get_value()
            section.set_end_point(fixed_point)
            sections.append(section)
            # start new section
            section = GuideSection()
            section.add_element(element)
            section.set_start_point(fixed_point)
        else:
            # continue current section
            section.add_element(element)

    # Finish last section
    section.set_end_point(total_length)
    sections.append(section)

    # Now have a list sections each of which have a fixed start and end point
    # Because they have fixed start and end, they are completely independent.

    # Extract instrument parameters fitting each section
    for section in sections:
        process_section(section, instrument_parameters)

    # Ensure all change points are set
    for index in range(len(elements)-1):
        current_element = elements[index]
        next_element = elements[index+1]

        current_element.next_start_point_parameter = next_element.start_point_parameter


class GuideSection:
    def __init__(self):
        """
        Simple container for elements where end points are well defined

        Container for elements where the first has a fixed start point, and the
        last element has a fixed end point (next_start_point parameter of last
        element has a fixed start).
        """
        self.elements = []
        self.start_point = None
        self.end_point = None

    def add_element(self, element):
        """
        Add an element to the section
        """
        self.elements.append(element)

    def get_elements(self):
        """
        Get list of elements in the section
        """
        return self.elements

    def set_start_point(self, start_point):
        """
        Set the start point of the section
        """
        self.start_point = start_point

    def set_end_point(self, end_point):
        """
        Set the end point of the section
        """
        self.end_point = end_point


def process_section(section, instrument_parameters):
    """
    Processes a section of a guide with fixed start and end

    A section is processed by providing start_point_parameter and
    next_start_point_parameter attributes to all the elements, these
    parameters have to fulfil all constraints given by the user under
    all legal configurations that can be provided by the optimizer.

    section: GuideSection object
        Section to be processed

    instrument_paramters: InstrumentParameterContainer object
        Instrument parameters where the parameters should be provided
    """
    elements = section.get_elements()

    # Add parameter describing the first start_point (always has fixed start)
    first_element = elements[0]

    par = first_element.start_point
    assert(is_fixed_parameter(par)) # Ensure the start point really is fixed
    instrument_parameters.add_parameter(par)
    first_element.start_point_parameter = par

    # If that was the only element in the section, no need to continue
    if len(elements) == 1:
        return

    # Find minimum value for first change point
    limiting_factors = [section.start_point]
    # If the second element has a free minimum start point defined, add that as limiting factor
    start_point_input = elements[1].start_point
    if is_free_parameter(start_point_input):
        min_start_point = start_point_input.get_lower_static_bound()
        if min_start_point is not None:
            limiting_factors.append(min_start_point)

    # If the first element has a minimum length defined, thats a limiting factor
    if is_free_parameter(first_element.length):
        min_length = first_element.length.get_lower_static_bound()
        if min_length is not None:
            limiting_factors.append(first_element.start_point.get_value() + min_length)

    # Limiting factor from end of section minus sum of lengths / max lengths
    sum, all_defined = sum_max_or_length(elements[1:])
    # Only apply this limit if all the lengths / max length were defined
    if all_defined:
        limiting_factors.append(section.end_point - sum)

    # Limiting factor for each min_start_point and unbroken max lengths / given lengths
    for index in range(1, len(elements)):
        element = elements[index]
        if is_free_parameter(element.start_point):
            min_start_point = element.start_point.get_lower_static_bound()
            if min_start_point is None:
                # No need to continue, this element doesnt have a min start point
                continue

        unbroken_max_length, unbroken = sum_max_or_length(elements[1:index])
        if unbroken:
            limiting_factors.append(min_start_point - unbroken_max_length)

    # Now the minimum allowed value for the first change point is the highest of the limiting factors
    minimum_first_cp = max(limiting_factors)

    # Find maximum value for first change point
    limiting_factors = [section.end_point]

    # If the second element has a free maximum start point defined, add that as limiting factor
    start_point_input = elements[1].start_point
    if is_free_parameter(start_point_input):
        max_start_point = start_point_input.get_upper_static_bound()
        if max_start_point is not None:
            limiting_factors.append(max_start_point)

    # If the first element has a maximum length defined, thats a limiting factor
    if is_free_parameter(first_element.length):
        max_length = first_element.length.get_upper_static_bound()
        if max_length is not None:
            limiting_factors.append(first_element.start_point.get_value() + max_length)

    # Limiting factor from end of section minus sum of lengths / min lengths
    total_min_length = sum_min_or_length(elements[1:])
    limiting_factors.append(section.end_point - total_min_length)

    # Limiting factor for each max_start_point and min lengths / given lengths
    for index in range(2, len(elements)):
        element = elements[index]
        if is_free_parameter(element.start_point):
            max_start_point = element.start_point.get_upper_static_bound()
            if max_start_point is not None:
                # This limiting factor is well defined
                total_min_length = sum_min_or_length(elements[1:index])
                limiting_factors.append(max_start_point - total_min_length)

    # Now the maximum allowed value for the first change point is the lowest of the limiting factors
    maximum_first_cp = min(limiting_factors)

    second_element = elements[1]
    par = ipars.RelativeFreeInstrumentParameter(second_element.name + "_start_point", minimum_first_cp, maximum_first_cp)
    second_element.start_point_parameter = par
    instrument_parameters.add_parameter(par)

    # Remaining change points from unitless parameters

    # These all need to have the static limiting factor found (which does not depend on optimizer choices)
    #  but will also depend on the choice in the optimizer. Use RelativeFreeInstrumentParameter

    for element_index in range(1, len(elements)-1):
        # Loop that create a parameter for the start point of the next element in the section
        # The loop uses information from the current element to specify the next elements start point

        current_element = elements[element_index]
        next_element = elements[element_index+1]
        element_name = current_element.name

        if is_fixed_parameter(current_element.length):
            # No need for a free parameter here, add a dependent parameter and continue
            length = current_element.length.get_value()
            start_point = current_element.start_point_parameter

            par = ipars.DependentInstrumentParameter(next_element.name + "_cp", start_point,
                                                     lambda l, cp: l + cp, constants=length)

            current_element.next_start_point_parameter = par
            next_element.start_point_parameter = par
            instrument_parameters.add_parameter(par)
            continue

        # The length is not fixed, need to find min and max static
        # Start with minimum from static conditions (depending on later elements)
        limiting_factors_static = [section.start_point]

        # Find previous min start point, as this start point must be above that
        for index in range(element_index, 1, -1):
            element = elements[index]
            if is_free_parameter(element.start_point):
                min_start_point = element.start_point.get_lower_static_bound()
                if min_start_point is not None:
                    limiting_factors_static.append(min_start_point)
                    break # Only the first defined minimum start point is relevant, as next will be further behind

        # End of section minus all max lengths / lengths can set a limiting factor
        total_max_length, all_defined = sum_max_or_length(elements[element_index+1:])
        if all_defined: # only if no elements with unbounded length
            limiting_factors_static.append(section.end_point - total_max_length)

        # For each later element in the section, an unbroken length of max lengths from that sets a min limit
        for index in range(element_index+1, len(elements)):
            element = elements[index]
            if is_free_parameter(element.start_point):
                min_start_point = element.start_point.get_lower_static_bound()
                if min_start_point is None:
                    # No need to continue, this element doesnt have a min start point
                    continue

            unbroken_max_length, unbroken = sum_max_or_length(elements[element_index+1:index])
            if unbroken:
                limiting_factors_static.append(min_start_point - unbroken_max_length)

        # minimum static limit is the most restrictive of the found limiting factors, so the maximum
        min_static_limit = max(limiting_factors_static)

        # Find the maximum static limit
        limiting_factors_static = [section.end_point]

        # Limiting factor from end of section minus sum of lengths / min lengths
        total_min_length = sum_min_or_length(elements[element_index+1:])
        limiting_factors_static.append(section.end_point - total_min_length)

        # Limiting factor for each max_start_point and min lengths / given lengths
        for index in range(element_index+1, len(elements)):
            element = elements[index]
            if is_free_parameter(element.start_point):
                max_start_point = element.start_point.get_upper_static_bound()
                if max_start_point is not None:
                    # This limiting factor is well defined
                    total_min_length = sum_min_or_length(elements[element_index+1:index])
                    limiting_factors_static.append(max_start_point - total_min_length)

        # maximum static limit is the most restrictive of the found limting factors, so the minimum
        max_static_limit = min(limiting_factors_static)

        # Define the parameter and add dynamic limits for possible min and max length
        par = ipars.RelativeFreeInstrumentParameter(next_element.name + "_cp", min_static_limit, max_static_limit)
        if is_free_parameter(current_element.length):
            min_length = current_element.length.get_lower_static_bound()
            if min_length is None:
                min_length = 0
            par.add_lower_dynamic(current_element.start_point_parameter, lambda x, a: x + a, constants=[min_length])

            max_length = current_element.length.get_upper_static_bound()
            if max_length is not None:
                par.add_upper_dynamic(current_element.start_point_parameter, lambda x, a: x + a, constants=[max_length])

        current_element.next_start_point_parameter = par
        next_element.start_point_parameter = par
        instrument_parameters.add_parameter(par)


def sum_max_or_length(elements):
    """
    Sums maximum lengths of elements

    The maximum length is only meaningful if all elements have
    a maximum length or fixed length defined. The logical variable
    returned is True if all elements had a maximum or fixed length.

    Returns both the sum and a logical variable
    """
    sum = 0
    all_defined = True
    for element in elements:
        if is_free_parameter(element.length):
            max_length = element.length.get_upper_static_bound()
            if max_length is not None:
                sum += max_length
            else:
                all_defined = False
        elif is_fixed_parameter(element.length):
            length = element.length.get_value()
            if length is not None:
                sum += length
            else:
                all_defined = False

    return sum, all_defined


def sum_min_or_length(elements):
    """
    Returns sum of minimum and fixed lengths of elements

    Elements without defined minimum length is considered 0 in the sum, and
    this thus always returns a useful value.
    """

    sum = 0
    for element in elements:
        if is_free_parameter(element.length):
            min_length = element.length.get_lower_static_bound()
            if min_length is not None:
                sum += min_length
        elif is_fixed_parameter(element.length):
            length = element.length.get_value()
            if length is not None:
                sum += length

    return sum


def is_fixed_parameter(parameter):
    """
    Checks if a parameter is fixed
    """
    return isinstance(parameter, ipars.FixedInstrumentParameter)


def is_free_parameter(parameter):
    """
    Checks if a parameter is free (Includes RelativeFreeInstrumentParameter)
    """
    return isinstance(parameter, ipars.FreeInstrumentParameter)


def propagate_fixed_lengths_to_start_points(elements, total_length):
    """
    Use fixed lengths to find additional fixed points

    If a fixed starting point is adjacent to a fixed length, a fixed starting
    point for that adjacent element can be calculated. This is done by looping
    from the start to the end, calculating start points in that direction, and
    then from the end to the start, calculating start points in that direction.
    The given list of elements has their start points overwritten by this
    function when they can be calculated from surrounding fixed points and
    lengths, it can happen this overwrites user input which was internally
    inconsistent.

    elements : list of Element objects
        The elements describing this guide

    total_length : float
        The distance from source to sample along the guide
    """
    # Set start point of guide to 0.0
    elements[0].start_point = ipars.FixedInstrumentParameter("start_point", 0.0)

    # Propagate fixed points from start using any fixed lengths next to fixed points.
    for index in range(len(elements) - 1):
        element = elements[index]
        next_element = elements[index + 1]
        # If this element has a known start and length, the next elements start can be calculated
        if is_fixed_parameter(element.start_point) and is_fixed_parameter(element.length):
            next_fixed_start = element.start_point.get_value() + element.length.get_value()
            # Assign known start point to next element
            if not is_fixed_parameter(next_element.start_point):
                par_name = next_element.name + "_fixed_start"
                next_element.start_point = ipars.FixedInstrumentParameter(par_name, next_fixed_start)
            else:
                # If a start point was already assigned, check it is consistent with calculation
                if next_element.start_point.get_value() != next_fixed_start:
                    raise RunTimeError("Error in input string, fixed start and fixed length disagrees")

    # Propagate fixed points from end to start using any fixed lengths next to fixed points.
    # First step manually using fixed total length
    """
    last_element = elements[-1]
    if is_fixed_parameter(last_element.length) and len(elements) > 1:
        second_to_last_element = elements[-2]
        calculated_start_point = total_length - last_element.length.get_value()
        if not is_fixed_parameter(second_to_last_element.start_point):
            par_name = second_to_last_element.name + "_fixed_start"
            second_to_last_element.start_point = ipars.FixedInstrumentParameter(par_name, calculated_start_point)
        else:
            if second_to_last_element.start_point.get_value() != calculated_start_point:
                raise RunTimeError("Error in input string, fixed start and fixed length disagrees")
    """
    last_element = elements[-1]
    if is_fixed_parameter(last_element.length) and len(elements) > 1:
        calculated_start_point = total_length - last_element.length.get_value()
        if not is_fixed_parameter(last_element.start_point):
            par_name = last_element.name + "_fixed_start"
            last_element.start_point = ipars.FixedInstrumentParameter(par_name, calculated_start_point)
        else:
            if last_element.start_point.get_value() != calculated_start_point:
                raise RunTimeError("Error in input string, fixed start and fixed length disagrees")

    # Next steps in for loop from end of guide to start
    for index in range(len(elements)-1, 1, -1):
        element = elements[index]
        previous_element = elements[index - 1]
        # If this element has a known start, and the previous has known length, the start of previous can be calculated
        if is_fixed_parameter(element.start_point) and is_fixed_parameter(previous_element.length):
            previous_fixed_start = element.start_point.get_value() - previous_element.length.get_value()
            if not is_fixed_parameter(previous_element.start_point):
                par_name = previous_element.name + "_fixed_start"
                previous_element.start_point = ipars.FixedInstrumentParameter(par_name, previous_fixed_start)
            else:
                # If a start point was already assigned, check it is consistent with calculation
                if previous_element.start_point.get_value() != previous_fixed_start:
                    raise RunTimeError("Error in input string, fixed start and fixed length disagrees")


