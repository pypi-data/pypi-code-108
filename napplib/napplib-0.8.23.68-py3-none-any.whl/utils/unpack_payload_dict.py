# build-in imports
import 	json

# external imports
from 	loguru 			import logger


__all__ = ('unpack_payload_dict')


@logger.catch()
def remove_null_dict(payload):
	remove_mapping = [None]
	for map_value in ['none', 'null']:
		remove_mapping.extend([map_value, map_value.capitalize, map_value.upper])

	if isinstance(payload, list):
		return [remove_null_dict(x) for x in payload if not x in remove_mapping]
	elif isinstance(payload, dict):
		return {
			key: remove_null_dict(val)
			for key, val in payload.items()
			if not val in remove_mapping
		}
	else:
		return payload


@logger.catch()
def unpack_payload_dict(payload, remove_null=False):
	"""[This function will turn the object into a json.]

	Args:
		payload (object): [A list of objects of type models to be transformed into json.]
		remove_null (bool, optional): [If True it will remove all Null/None keys and values.]. Defaults to False.

	Raises:
		Exception: [An error will be raised if it is not possible to convert to json.]

	Returns:
		[json]: [The converted json]
	"""
	try: 
		payload_json = json.dumps(payload, ensure_ascii=False, default = lambda o: o.__dict__) if not isinstance(payload, str) else payload
		return payload_json if not remove_null else json.dumps(remove_null_dict(json.loads(payload_json)))
	except json.JSONDecodeError:
		raise Exception(f'{type(payload)} cannot be turned into a json')
