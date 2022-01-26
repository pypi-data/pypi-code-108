from django.test import TestCase
from eveuniverse.tools.testdata import ModelSpec, create_testdata

from . import test_data_filename


class CreateEveUniverseTestData(TestCase):
    def test_create_testdata(self):
        testdata_spec = [
            ModelSpec("EveType", ids=[35832, 35825, 35835]),
            ModelSpec("EveSolarSystem", ids=[30004984, 30045339]),
        ]
        create_testdata(testdata_spec, test_data_filename())
