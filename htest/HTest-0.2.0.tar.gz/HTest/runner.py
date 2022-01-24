#!/usr/bin/env python3.7
# encoding: utf-8
from .loader import Loader


class Runner(object):

    def __init__(self, path):
        self.path = path

    def run(self):
        loader = Loader()
        loader.load(self.path)

        for test_class, test_cases in loader:
            test_instance = test_class(test_class.__name__)
            test_instance.setup()

            try:
                for test_case in test_cases:
                    test_case(test_instance)
            except AttributeError:
                raise

            test_instance.teardown()


main = Runner
