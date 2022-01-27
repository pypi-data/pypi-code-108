class TupleTypeError(Exception):
    """tuple_convert handle when passed an unknown type"""
    def __init__(self, variable):
        super(TupleTypeError, self).__init__(
            f"\n\tExpected a string of a tuple yet found {type(variable)}\n\ttuple_convert will not raise this error "
            f"for non-string lists or tuples by default but this can be enabled by setting must_be_string to True")


class SubListsNotEqualLength(Exception):
    def __init__(self, sub_lengths):
        super(SubListsNotEqualLength, self).__init__(
            f"\n\tflip_lists requires all sub lists to be of equal length yet found:"
            f"\n\tList Lengths -> {sub_lengths}"
        )


class InvalidDateType(Exception):
    def __init__(self, method_name, dates_list):
        super(InvalidDateType, self).__init__(
            f"\n\t{method_name} takes a expects a str, list, or tuple yet found {type(dates_list)}"
        )


class InvalidBool(Exception):
    def __init__(self, bool_var):
        super(InvalidBool, self).__init__(
            f"\n\tstring_to_bool requires the variable to be a string or a bool yet was passed {type(bool_var)}")