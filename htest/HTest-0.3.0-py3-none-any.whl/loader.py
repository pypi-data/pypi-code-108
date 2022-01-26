#!/usr/bin/env python3.7
# encoding: utf-8
import importlib
from .basepage import BasePage


def find_test_method(test_class):
    test_methods = []

    for method in dir(test_class):
        if method.startswith("test"):
            test_methods.append(
                getattr(test_class, method)
            )
    return test_methods


class Loader(object):
    def __init__(self):
        self.cases = {}

    def load(self, path):
        module = importlib.import_module(path)
        for test_class_name in dir(module):
            test_class = getattr(module, test_class_name)
            if isinstance(test_class, type) and issubclass(test_class, BasePage):
                self.cases.update({
                    test_class: find_test_method(test_class) or []
                })

    def __iter__(self):
        for test_class, test_cases in self.cases.items():
            yield test_class, test_cases
