import pickle
from .logger import logger

def isPicklable(item) -> bool:
	try:
		_ = pickle.dumps(item)
		return True
	except Exception as e:
		logger.debug(f"Item is not pickable: {e}")
		return False
