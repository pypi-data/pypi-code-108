"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""
from typing import Any, Dict, List, Callable


class DynamicClass(object):
    """ Allow a class to have new methods added dynamically. """

    def _wrap_function_with_kwargs_and_add_to_class(
        self,
        fn_name: str,
        fn_to_wrap: Callable,
        kwargs_dict: Dict[str, Any],
        docstring: str,
    ) -> List[Exception]:
        try:

            def dynamic_method(**kwargs):
                for k in kwargs.keys():
                    if k not in kwargs_dict:
                        raise TypeError(
                            "{}() got an unexpected keyword argument '{}'".format(
                                fn_name, k
                            )
                        )
                return fn_to_wrap(**kwargs)

            dynamic_method.__doc__ = docstring
            self._add_function_to_class(fn_name, dynamic_method)
            return []
        except Exception as e:
            print("Failed to dynamically generate `{}`".format(fn_name), e)
            return [e]

    def _add_function_to_class(self, fn_name: str, fn: Callable):
        """ Add a specified bit of code as a function to the current class """
        fn.__name__ = fn_name
        return setattr(self, fn_name, fn)
