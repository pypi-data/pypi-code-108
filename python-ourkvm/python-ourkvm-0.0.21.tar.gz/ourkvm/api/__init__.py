import sys
import urllib.error
from fastapi import Depends, FastAPI
from typing import Dict, Any
from ..storage import storage

if storage['arguments'].api or 'sphinx' in sys.modules:
	from .app import app as app
	from .security import User as User
	from .security import process_user_claim as process_user_claim
	from .networking import get_network_interface_info
	from .qemu import create_machine_configuration
	from .resources import create_virtual_harddrive
	from .capabilities import get_network_interface_arguments
	from .monitoring import get_machines_health

	@app.get("/users/me")
	def get_current_user_information(current_user: User = Depends(process_user_claim)) -> User:
		"""
		This API call will return the current (logged in) user information.
		"""
		return current_user

	@app.get("/clusters")
	def list_all_known_cluster_nodes(current_user: User = Depends(process_user_claim)) -> Dict[str, Any]:
		"""
		List all available clusters (if any).
		"""
		return {}

	@app.options("/online")
	def check_api_responsiveness() -> bool:
		"""
		Returns true if we're alive
		"""
		return True

	import sys
	# Avoid running uvicorn if pytest is being executed.
	if "pytest" not in sys.modules and 'sphinx' not in sys.modules:
		import uvicorn
		uvicorn.run(app)