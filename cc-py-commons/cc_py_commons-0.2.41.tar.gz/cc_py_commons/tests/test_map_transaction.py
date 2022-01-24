from uuid import UUID
import datetime
import unittest

from cc_py_commons.loads.location import Location
from cc_py_commons.loads.equipment import Equipment
from cc_py_commons.loads.load import Load
from cc_py_commons.transactions.map_transaction import from_load

class TestMapTransaction(unittest.TestCase):

	def setUp(self):
		self.valid_load = Load(reference_number='20067', 
			customer_id=5876, 
			origin=Location(city='PLYMOUTH', state='NC', postcode='27962', county=None, country=None, latitude=None, longitude=None), 
			destination=Location(city='COLLEGE PARK', state='GA', postcode='30349', county=None, country=None, latitude=None, longitude=None), 
			pickup_date=datetime.date(2021, 7, 23), 
			delivery_date=datetime.date(2021, 7, 23), 
			status_id=UUID('9bcd4613-831e-4cb4-a76f-9166ce559fa6'), 
			source_id=UUID('03caea36-98c9-46f6-aa9c-a102576bc185'), 
			equipment=[Equipment(id='836284b0-f1ae-4f78-83e6-93f81b4c22c9', name='REEFER')], 
			equipment_description='REEFER', 
			contact=None, 
			pickup_open_time=datetime.time(0, 1), 
			pickup_close_time=None, 
			pickup_appointment_required=True, 
			delivery_open_time=datetime.time(0, 1), 
			delivery_close_time=None, 
			delivery_appointment_required=True, 
			tracking_number=None, 
			full_load=True, 
			length=None, 
			width=None, 
			height=None, 
			weight=35078.0,
			load_count=None, 
			distance=534.0, 
			stops=2, 
			rate=138786, 
			declared_value=None, 
			comment=None, 
			commodity='Nuts', 
			min_temperature=60.0, 
			max_temperature=None, 
			tarp_size=None, 
			carrier_id=None, 
			contact_id=None, 
			url=None, 
			demo_load=False, 
			team_service_required=False, 
			quote_id=None, 
			truck_lane_search_id=None, 
			truck_search_id=None, 
			id=None,
			load_number=None, 
			mcleod_movement_id='20067')

	def test_valid_load(self):
		t = from_load(self.valid_load)
		print(t)
		self.assertEqual(self.valid_load.reference_number, t.reference_number)
