# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from functools import wraps
from tcell_agent.instrumentation.utils import module_name, skip_instrumentation
from tcell_agent.tcell_logger import get_module_logger


class InstrumentedMethod(object):
    def __init__(self, obj, func_name, target):
        self.obj = obj
        self.func_name = func_name
        self.target = target


class InstrumentationManager(object):
    _instrumented = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.reset()

    @classmethod
    def instrument(cls, original_object, original_method_str, new_method):
        logger = get_module_logger(__name__)
        module_name_str = module_name(original_object)
        full_func_name = "{}.{}".format(module_name_str, original_method_str)

        if module_name_str and skip_instrumentation(module_name_str, original_method_str):
            if logger is not None:
                logger.info("Skipping instrumentation for method: {}".format(full_func_name))
                return

        target_method = getattr(original_object, original_method_str)
        already_wrapped = hasattr(target_method, "__tcell_instrumentation__original_method__")
        if already_wrapped:
            return

        @wraps(target_method)
        def wrapped_func(*args, **kwargs):
            return new_method(target_method, *args, **kwargs)

        wrapped_func.__tcell_instrumentation__original_method__ = target_method
        wrapped_func.__tcell_instrumentation__original_object__ = original_object
        wrapped_func.__tcell_instrumentation__original_method_str__ = original_method_str
        wrapped_func.__tcell_instrumentation__new_method__ = new_method

        setattr(original_object, original_method_str, wrapped_func)
        cls._instrumented[wrapped_func] = (original_object, original_method_str, target_method)

        if logger is not None:
            logger.info("Instrumenting method: {}".format(full_func_name))

    @classmethod
    def is_instrumented(cls, target_method):
        already_wrapped = hasattr(target_method, "__tcell_instrumentation__original_method__")
        return already_wrapped

    @classmethod
    def remove_instrumentation(cls, original_object, original_method_str, target_method):
        setattr(original_object, original_method_str, target_method)

    @classmethod
    def reset(cls):
        for _, value in cls._instrumented.items():
            original_object, original_method_str, target_method = value
            cls.remove_instrumentation(original_object, original_method_str, target_method)
