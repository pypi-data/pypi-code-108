from collections import OrderedDict, defaultdict
from typing import Union, Optional

from jb_misc_lib.core import defaultNoneDict


# TODO: Condition checker -> list of functions that recieve all arguments and must return true


class CheckError(BaseException):
    def __init__(self, func, message: str):
        self._func = func
        super().__init__(message)


class ConditionCheckError(CheckError):
    def __init__(self, func, condition_desc, args, kwargs):
        self.condition_description = condition_desc
        self.condition_args = args
        self.condition_kwargs = kwargs
        message = f"\nCondition: {condition_desc}, was not satisfied in function {func.__name__}"
        super().__init__(func, message)


class ElementCheckError(CheckError):
    def __init__(self, func, element, element_desc: str, message: str):
        self.element = element
        self.element_desc = element_desc
        super().__init__(func, message)


class TypeCheckError(ElementCheckError):
    def __init__(self, func, element, valid_types: list[type], element_desc: str):
        self.valid_types = valid_types
        message = f"""
{element_desc} of {func.__name__} was an invalid type of {type(element).__name__}, \
valid types are: {', '.join([x.__name__ for x in valid_types])}"""
        super().__init__(func, element, element_desc, message)


class PropertyCheckError(ElementCheckError):
    def __init__(self, func, element, required_property: str, element_desc: str):
        self.required_property = required_property
        message = f"""
{element_desc} of {func.__name__} of type {type(element).__name__} \
does not have property {required_property}"""
        super().__init__(func, element, element_desc, message)


class BaseCheck:
    def __init__(self,
                 clean_arg_types: Union[list[Optional[list[type]]], list[None]],
                 clean_arg_properties: Union[list[Optional[list[str]]], list[None]],
                 clean_kwarg_types: Union[defaultdict[str, list[type]],
                                          defaultdict[str, None]],
                 clean_kwarg_properties: Union[defaultdict[str, list[str]],
                                               defaultdict[str, None]],
                 return_types: Optional[list[type]] = None,
                 return_properties: Optional[list[str]] = None,
                 input_conditions: Optional[list[dict]] = None,
                 output_conditions: Optional[list[dict]] = None,
                 type_checker_active: bool = True):

        # Type annotations can check other args but we need to verify the condition lists
        def check_condition_arg(cnd_dict_list):
            for cnd_dict in cnd_dict_list:
                if "msg" not in cnd_dict.keys() and "func" not in cnd_dict.keys():
                    raise Exception("Type check didn't have \"msg\" and \"func\" in all conditions")

        if input_conditions is not None:
            check_condition_arg(input_conditions)

        if output_conditions is not None:
            check_condition_arg(output_conditions)

        self.active = type_checker_active
        self._arg_types = clean_arg_types
        self._arg_properties = clean_arg_properties
        self._kwarg_types = clean_kwarg_types
        self._kwarg_properties = clean_kwarg_properties
        self._return_types = return_types
        self._return_properties = return_properties
        self._input_conditions = input_conditions
        self._output_conditions = output_conditions
        self._func = None


    def check_datum(self, datum,
                    valid_types: Optional[list[type]],
                    required_properties: Optional[list[str]],
                    fail_data_str: str):

        # Check datum is of a valid type if there are type restrictions
        if valid_types is not None and not any([isinstance(datum, t) for t in valid_types]):
            raise TypeCheckError(self._func, datum, valid_types, fail_data_str)

        # Check datum has all require properties
        if required_properties is not None:
            for _property in required_properties:
                if not hasattr(datum, _property):
                    raise PropertyCheckError(self._func, datum, _property, fail_data_str)


    def check_condition(self, message, func, *args, **kwargs):
        if not func(*args, **kwargs):
            raise ConditionCheckError(func, message, args, kwargs)


    def __call__(self, func):
        self._func = func

        def wrapper(*args, **kwargs):
            if self.active:

                # Check positional args
                arg_triples = zip(args, self._arg_types, self._arg_properties)
                for i, (arg, valid_types, properties) in enumerate(arg_triples):
                    self.check_datum(arg, valid_types, properties, f"Position argument {i}")

                # Check keyword args, rearranging checks could increase efficiency
                for k_name, k_val in kwargs.items():
                    valid_types = self._kwarg_types[k_name]
                    properties = self._kwarg_properties[k_name]
                    self.check_datum(k_val, valid_types, properties, f"Keyword argument {k_name}")

                # Check conditions on input args
                if self._input_conditions is not None:
                    for cnd_dict in self._input_conditions:
                        self.check_condition(cnd_dict["msg"], cnd_dict["func"], *args, **kwargs)

                # Perform function call
                return_obj = func(*args, **kwargs)

                # Check return data
                self.check_datum(return_obj, self._return_types, self._return_properties,
                                 "Return object")

                # Check conditions on output
                if self._output_conditions is not None:
                    for cnd_dict in self._output_conditions:
                        self.check_condition(cnd_dict["msg"], cnd_dict["func"], return_obj)

            # Inactive so just call and pass on the return object
            else:
                return_obj = func(*args, **kwargs)

            return return_obj
        return wrapper


class GeneralCheck(BaseCheck):
    def __init__(self,
                 arg_types: Union[OrderedDict[str, Optional[list[type]]], None] = None,
                 arg_properties: Union[OrderedDict[str, Optional[list[str]]], None] = None,
                 return_types: Optional[list[type]] = None,
                 return_properties: Optional[list[str]] = None,
                 input_conditions: Optional[list[dict]] = None,
                 output_conditions: Optional[list[dict]] = None,
                 type_checker_active: bool = True):

        """Decorator for checking types, properties and conditions on function call / return

        Args:
            arg_types:   OrderedDict[str, list[type]]
                OrderedDict containing valid input types for each argument
                The order forms a list to check args and dict is used to check kwargs

            arg_properties:  OrderedDict[str, list[str]]
                OrderedDict containing properties each argument must have
                The order forms a list to check args and dict is used to check kwargs

            return_types:    list[type]
                A list of valid return types from the function
                None means no check is made
                Empty list will be interpreted as no possible valid types

            return_properties:  list[str]
                A list of required properties of the return type
                None or empty list means no check is made

            type_checker_active: bool
                Whether or not to perform type checks
                As type checks are runtime they can be disabled for performance

            input_conditions: list[dict[str, function]]
                A dictionary containing functions and messages
                The function takes all args and kwargs, if it returns falsy then error is thrown
                The message is used to describe the condition in the error for user feedback

            output_conditions: list[dict[str, function]]
                Same as input_conditions except the function takes the return_object as an argument
        """

        # This helps us streamline and type check the checking code
        if arg_types is None and arg_properties is None:
            clean_arg_types = []
            clean_arg_properties = []

        else:

            if arg_types is None and arg_properties is not None:
                clean_arg_types = [None for _ in arg_properties.values()]
                clean_arg_properties = list(arg_properties.values())

            elif arg_types is not None and arg_properties is None:
                clean_arg_types = list(arg_types.values())
                clean_arg_properties = [None for _ in arg_types.values()]

            # Superfluous check but allows for linter to confirm type safety
            elif arg_types is not None and arg_properties is not None:
                clean_arg_types = list(arg_types.values())
                clean_arg_properties = list(arg_properties.values())

            else:
                raise Exception("Unexpected branch, there's a bug in this code")

        clean_kwarg_types = defaultNoneDict(arg_types)
        clean_kwarg_properties = defaultNoneDict(arg_properties)

        super().__init__(
            clean_arg_types=clean_arg_types, clean_arg_properties=clean_arg_properties,
            clean_kwarg_types=clean_kwarg_types, clean_kwarg_properties=clean_kwarg_properties,
            return_types=return_types, return_properties=return_properties,
            input_conditions=input_conditions, output_conditions=output_conditions,
            type_checker_active=type_checker_active
        )


# For just asserting a single type for each element
class TypeCheck(BaseCheck):
    def __init__(self, *args: type, return_type: type = None,
                 type_checker_active: bool = True, **kwargs: type):
        return_types = None if return_type is None else [return_type]
        clean_kwarg_types = defaultNoneDict({k: [t] for k, t in kwargs.items()})

        super().__init__(clean_arg_types=[[x] for x in args],
                         clean_arg_properties=[None for _ in args],
                         clean_kwarg_types=clean_kwarg_types,
                         clean_kwarg_properties=defaultdict(lambda: None),
                         return_types=return_types,
                         return_properties=None,
                         type_checker_active=type_checker_active)

