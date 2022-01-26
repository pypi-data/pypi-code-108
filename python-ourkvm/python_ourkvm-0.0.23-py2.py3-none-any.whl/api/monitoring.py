import glob
import json
import pathlib
from typing import Dict, Any, Generator, Optional
from fastapi import Security, Request
from .security import User, process_user_claim
from .app import app
from ..lib.helpers.logger import log
from ..lib.qemu.qemu import get_machine_disk_information

machine_health_database :Dict[str, Any] = {}
access_tokens :Dict[str, str] = {
	'1234' : 'testmachine'
}

def access_token_to_machine_name(access_token :str) -> Optional[str]:
	return access_tokens.get(access_token, None)

@app.get("/monitoring/machines/health", tags=["monitoring"])
def get_machines_health(current_user: User = Security(process_user_claim, scopes=["monitoring*"])) -> Generator[Dict[str, Any], None, None]:
	"""
	This endpoint returns the current health of all machines
	"""

	for machine_config_path in glob.glob("/etc/qemu.d/*.cfg"):
		with open(machine_config_path) as fh:
			try:
				machine_conf = json.load(fh)
			except:
				log(f"Could not load JSON configuration found at: {machine_config_path}")
				continue

		machine_name = machine_conf.get('name', pathlib.Path(machine_config_path).name[:-4])
		disk_information = get_machine_disk_information(machine_conf.get('name', pathlib.Path(machine_config_path).name[:-4]))

		yield {
			'name': machine_name,
			'harddrives': disk_information,
			'interfaces': [],
			'memory': {},
			'cpu': {},
			'os' : None,
			**machine_health_database.get(machine_name, {})
		}

@app.put("/monitoring/machine/health", tags=["monitoring"])
def report_in_machine_health(access_token :str, data :Dict[str, Any], request: Request) -> None:
	"""
	This endpoint is used to report in health data from a system
	"""
	agent_ip = request.client.host
	agent_name = access_token_to_machine_name(access_token)
	
	if agent_name:
		machine_health_database[agent_name] = {
			**data,
			'name' : agent_name,
			'last_seen' : agent_ip
		}