from unittest import TestCase
from .grape import GeneralGraph


class TestGeneralGraph(TestCase):
    """
    Class TestGeneralGraph to check creating an instance of
    GeneralGraph object
    """
    def create_instance(self):
        GeneralGraph()
