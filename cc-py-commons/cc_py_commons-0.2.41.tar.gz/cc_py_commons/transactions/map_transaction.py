from dataclasses import fields
from cc_py_commons.transactions.transaction import Transaction

def from_load(load):
	"""Takes a freight-hub load and maps it to a pricing load (Transaction)"""
	trans_data = {}

	for field in fields(Transaction):
		value = getattr(load, field.name, None)
		
		if value:
			trans_data[field.name] = value
			
	trans_data['equipment'] = load.equipment_description
	trans_data['all_in_cost'] = load.rate # all in cost may change at booking
	trans_data['target_pay'] = load.rate # target_pay is what the broker listed the load for
	trans_data['multi_stop'] = load.stops
	trans_data['team_service'] = load.team_service_required

	if isinstance(load.origin, dict):
		trans_data['origin_city'] = load.origin['city']
		trans_data['origin_state'] = load.origin['state']
		trans_data['origin_postcode'] = load.origin['postcode']
	else:
		trans_data['origin_city'] = load.origin.city
		trans_data['origin_state'] = load.origin.state
		trans_data['origin_postcode'] = load.origin.postcode

	if isinstance(load.destination, dict):
		trans_data['destination_city'] = load.destination['city']
		trans_data['destination_state'] = load.destination['state']
		trans_data['destination_postcode'] = load.destination['postcode']
	else:
		trans_data['destination_city'] = load.destination.city
		trans_data['destination_state'] = load.destination.state
		trans_data['destination_postcode'] = load.destination.postcode

	del trans_data['customer_id']
	trans_data['client_id'] = None
	trans_data['equipment_class'] = None
	transaction = Transaction(**trans_data)
	return transaction
