"""TestInputGraph to check input of GeneralGraph"""

from unittest import TestCase
from grape.general_graph import GeneralGraph


class TestInputGraph(TestCase):
    """
	Class TestInputGraph to check input of GeneralGraph
	"""

    def test_Mark(self):
        """
		Unittest check for mark attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        mark_dict = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19'
        }

        self.assertDictEqual(mark_dict, g.mark, msg="Wrong MARK in input")

    def test_father_condition(self):
        """
		Unittest check for father_condition attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        cond_dict = {
            ('1', '2'): 'SINGLE',
            ('1', '3'): 'SINGLE',
            ('2', '4'): 'SINGLE',
            ('3', '5'): 'SINGLE',
            ('4', '6'): 'SINGLE',
            ('5', '11'): 'AND',
            ('6', '7'): 'SINGLE',
            ('6', '8'): 'SINGLE',
            ('7', '6'): 'SINGLE',
            ('8', '6'): 'SINGLE',
            ('8', '9'): 'OR',
            ('9', '16'): 'SINGLE',
            ('10', '11'): 'AND',
            ('11', '19'): 'SINGLE',
            ('12', '13'): 'SINGLE',
            ('12', '19'): 'SINGLE',
            ('13', '12'): 'SINGLE',
            ('13', '14'): 'SINGLE',
            ('14', '13'): 'SINGLE',
            ('14', '18'): 'SINGLE',
            ('14', '19'): 'SINGLE',
            ('15', '9'): 'OR',
            ('16', '17'): 'SINGLE',
            ('17', '10'): 'SINGLE',
            ('17', '16'): 'SINGLE',
            ('19', '12'): 'SINGLE',
            ('19', '14'): 'SINGLE'
        }

        self.assertDictEqual(cond_dict, g.father_condition,
        msg="Wrong FATHER CONDITION in input")

    def test_area(self):
        """
		Unittest check for area attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        area_dict = {
            '1': 'area1',
            '2': 'area1',
            '3': 'area1',
            '4': 'area1',
            '5': 'area1',
            '6': 'area4',
            '7': 'area4',
            '8': 'area4',
            '9': 'area3',
            '10': 'area3',
            '11': 'area2',
            '12': 'area2',
            '13': 'area2',
            '14': 'area2',
            '15': 'area3',
            '16': 'area3',
            '17': 'area3',
            '18': 'area2',
            '19': 'area2'
        }

        self.assertDictEqual(area_dict, g.area, msg="Wrong AREA in input")

    def test_perturbation_resistant(self):
        """
		Unittest check for perturbation_resistant attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        perturbation_resistant_dict = {
            '1': [''],
            '2': ['perturbation1'],
            '3': ['perturbation1'],
            '4': ['perturbation1'],
            '5': ['perturbation1'],
            '6': [''],
            '7': [''],
            '8': [''],
            '9': [''],
            '10': [''],
            '11': [''],
            '12': [''],
            '13': [''],
            '14': [''],
            '15': [''],
            '16': [''],
            '17': [''],
            '18': [''],
            '19': ['']
        }

        self.assertDictEqual(
            perturbation_resistant_dict,
            g.perturbation_resistant,
            msg="Wrong PERTURBATION RESISTANT in input")

    def test_init_status(self):
        """
		Unittest check for init_status attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        init_status_dict = {'2': True, '3': True}

        self.assertDictEqual(init_status_dict, g.init_status,
            msg="Wrong INIT STATUS in input")

    def test_description(self):
        """
		Unittest check for description attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        description_dict = {
            '1': '',
            '2': '',
            '3': '',
            '4': '',
            '5': '',
            '6': '',
            '7': '',
            '8': '',
            '9': '',
            '10': '',
            '11': '',
            '12': '',
            '13': '',
            '14': '',
            '15': '',
            '16': '',
            '17': '',
            '18': '',
            '19': ''
        }

        self.assertDictEqual(description_dict, g.description,
            msg=" Wrong DESCRIPTION in input ")

    def test_type(self):
        """
		Unittest check for type attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        type_dict = {
            '1': 'SOURCE',
            '2': 'SWITCH',
            '3': 'SWITCH',
            '4': 'HUB',
            '5': 'HUB',
            '6': 'HUB',
            '7': 'HUB',
            '8': 'HUB',
            '9': 'HUB',
            '10': 'HUB',
            '11': 'HUB',
            '12': 'HUB',
            '13': 'HUB',
            '14': 'HUB',
            '15': 'SOURCE',
            '16': 'HUB',
            '17': 'HUB',
            '18': 'USER',
            '19': 'HUB'
        }

        self.assertDictEqual(type_dict, g.type, msg="Wrong TYPE in input")

    def test_weight(self):
        """
		Unittest check for Weight attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        weight_dict = {
			('1', '2'): 1.0,
			('1', '3'): 1.0,
			('2', '4'): 1.0,
			('3', '5'): 1.0,
			('4', '6'): 1.0,
			('5', '11'): 1.0,
			('6', '7'): 1.0,
			('6', '8'): 1.0,
			('7', '6'): 1.0,
			('8', '6'): 1.0,
			('8', '9'): 1.0,
			('9', '16'): 1.0,
			('15', '9'): 1.0,
			('16', '17'): 1.0,
			('17', '16'): 1.0,
			('17', '10'): 1.0,
			('10', '11'): 1.0,
			('11', '19'): 1.0,
			('19', '12'): 1.0,
			('19', '14'): 1.0,
			('12', '19'): 1.0,
			('12', '13'): 1.0,
			('14', '19'): 1.0,
			('14', '13'): 1.0,
			('14', '18'): 1.0,
			('13', '12'): 1.0,
			('13', '14'): 1.0
        }

        self.assertDictEqual(weight_dict, g.weight, msg="Wrong WEIGHT in input")

    def test_initial_service(self):
        """
		Unittest check for initial_service attribute of GeneralGraph:
		correct input reading.
		"""
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        initial_service_dict = {
            '1': 1.0,
            '2': 0.0,
            '3': 0.0,
            '4': 0.0,
            '5': 0.0,
            '6': 0.0,
            '7': 0.0,
            '8': 0.0,
            '9': 0.0,
            '10': 0.0,
            '11': 0.0,
            '12': 0.0,
            '13': 0.0,
            '14': 0.0,
            '15': 2.0,
            '16': 0.0,
            '17': 0.0,
            '18': 0.0,
            '19': 0.0
        }

        self.assertDictEqual(initial_service_dict, g.initial_service,
            msg=" Wrong INITIAL SERVICE in input ")

    def test_initial_sources(self):
        """
        Unittest check for sources of GeneralGraph: correct input reading.
        """
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        self.assertEqual(['1', '15'], g.sources, msg=" Wrong SOURCES in input ")

    def test_initial_hubs(self):
        """
        Unittest check for hubs of GeneralGraph: correct input reading.
        """
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        self.assertEqual(['4', '5', '6', '7', '8', '9', '16', '17', '10', '11',
            '19', '12', '14', '13'], g.hubs, msg=" Wrong HUBS in input ")

    def test_initial_users(self):
        """
        Unittest check for users of GeneralGraph: correct input reading.
        """
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        self.assertEqual(['18'], g.users, msg=" Wrong USERS in input ")

    def test_initial_switches(self):
        """
        Unittest check for switches of GeneralGraph: correct input reading.
        """
        g = GeneralGraph()
        g.load("tests/TOY_graph.csv")

        self.assertEqual(['2', '3'], g.switches,
            msg=" Wrong SWITCHES in input ")
