from typing import Type, Dict, Callable, Set, Optional, Any

from enginelib.claim_focus import ClaimFocus
from enginelib.claim_line_focus import ClaimLineFocus

from enginelib.decor.errors import InvalidParameterError
from enginelib.decor.registry import Registry


class Predicate:
    """Wraps a function that was decorated with @Tree.node

    At the time of creation, checks whether the given
    function has its return type annotated and whether
    the parameters it accepts are allowed and if their
    types annotated and corresponds to what is expected.

    It supports verification of pre-determined parameters
    and also custom parameters (defined by the developer).
    """

    allowed_standard_params: Dict[str, Type] = {
        'cue': ClaimFocus,
        'oc': ClaimFocus,
        'clue': ClaimLineFocus,
        'ocl': ClaimLineFocus,
        'ocl_s': ClaimLineFocus,
        'ocl_d': ClaimLineFocus,
        'acl': ClaimLineFocus,
        'registry': Registry,
        'data': Dict[str, Any]
    }
    """These are the names of the pre determined parameters
    that are allowed for the wrapped function and their 
    expected types."""

    def __init__(self,
                 func: Callable[..., bool],
                 allowed_custom_params: Optional[Dict[str, Type]] = None,
                 require_return_bool: bool = True):
        #: the function being wrapped.
        self.func = func

        #: the names and types of custom parameters allowed
        #: for the function being wrapped.
        self.allowed_custom_params: Dict[str, Type] = allowed_custom_params or dict()

        #: the actual set of standard parameters that the function
        #: being wrapped takes
        self.standard_params: Set[str] = set()

        #: the actual set of custom parameters that the function
        #: being wrapped takes
        self.custom_params: Set[str] = set()
        self._examine_annotations(require_return_bool)

    @property
    def description(self) -> str:
        """The textual description of the node being implemented
        by the wrapped function.

        It is extracted from the function's docstring.
        """
        return self.func.__doc__

    def _validate_parameter(self, param_name: str, param_type: Type):
        if param_name in self.allowed_standard_params:
            expected_param_type = self.allowed_standard_params[param_name]
        elif param_name in self.allowed_custom_params:
            expected_param_type = self.allowed_custom_params[param_name]
        else:
            raise InvalidParameterError(
                message=f'Custom parameter "{param_name}" must be defined before it can be used.')

        if expected_param_type is not param_type:
            raise InvalidParameterError(
                message=f'Parameter "{param_name}" must have annotated type "{expected_param_type.__name__}".')

    def _examine_annotations(self, require_return_bool: bool = True):
        func = self.func

        if require_return_bool:
            assert 'return' in func.__annotations__, 'Predicate functions must have return type annotated as bool.'
            assert func.__annotations__['return'] is bool, 'Predicate functions must return bool.'

        for param_name, param_type in func.__annotations__.items():
            if param_name == 'return':
                continue

            self._validate_parameter(param_name, param_type)
            if param_name in self.allowed_standard_params:
                self.standard_params.add(param_name)
            else:
                self.custom_params.add(param_name)

        # checks whether the developer has used more than one filtering parameter:
        if len(self.standard_params.intersection({'oc', 'ocl', 'ocl_d', 'ocl_s', 'acl'})) > 1:
            raise InvalidParameterError('Only one of {oc, ocl, ocl_d, ocl_s, acl} '
                                        'may appear as a parameter in a predicate function.')
