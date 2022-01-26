from fastapi import Security, HTTPException
from typing import Dict, Any, List, Union
from pydantic import BaseModel
from typing import Optional
from .security import User, process_user_claim
from .app import app
from ..lib.networking import ip, get_interface_info, create_interface, add_namespace, get_namespace_info, del_namespace
from ..lib.helpers.exceptions import InterfaceNotFound, NamespaceNotFound

class NewInterface(BaseModel):
	iftype: str
	mac: Optional[str] = None
	ip: Optional[str] = None
	netmask: Optional[str] = None
	state: Optional[str] = "up"

@app.get("/networking/interface/{ifname}", tags=["networking"])
def get_network_interface_info(ifname :str, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> List[Dict[str, Union[int, None, str]]]:
	"""
	Returns networking information for the given interface.
	The result will be a list of addresses:

	```json
	[
		{"mac": "address"},
		{"ipv4": "address"},
		...
	]
	```
	"""
	try:
		return list(get_interface_info(ifname))
	except InterfaceNotFound:
		raise HTTPException(status_code=404, detail="Interface not found")

@app.put("/networking/interface/{ifname}", tags=["networking"])
def create_new_interface(ifname :str, info :NewInterface, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> List[Dict[str, Union[int, None, str]]]:
	"""
	This API can be used to create interfaces
	"""
	try:
		list(get_interface_info(ifname))
	except InterfaceNotFound:
		create_interface(ifname, info.iftype)
	
	return list(get_interface_info(ifname))

@app.delete("/networking/interface/{ifname}", tags=["networking"])
def delete_interface(ifname :str, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> List[Dict[str, Union[int, None, str]]]:
	"""
	This API can be used to delete interfaces
	"""
	try:
		if list(get_interface_info(ifname)):
			ip.link(f"del {ifname}")

			return list(get_interface_info(ifname))

		raise HTTPException(status_code=404, detail="Interface could not be found after creation.")
	except InterfaceNotFound:
		return []

@app.put("/networking/namespace/{name}", tags=["networking"])
def create_new_namespace(name :str, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> Dict[str, Any]:
	"""
	This API can be used to create namespaces.
	"""
	add_namespace(name)
	
	return get_namespace_info(name)

@app.delete("/networking/namespace/{name}", tags=["networking"])
def delete_namespace(name :str, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> Dict[str, Any]:
	"""
	This API can be used to delete namespaces.
	"""
	del_namespace(name)
	
	try:
		return get_namespace_info(name)
	except NamespaceNotFound:
		return {}

@app.patch("/networking/interface/{name}/connect/{master}", tags=["networking"])
def set_master_on_interface(name :str, master :str, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> bool:
	"""
	This API endpoint can be used to set a `master` on a given interface name.
	"""
	return bool(ip.link(f"set dev {name} master {master}").exit_code == 0)

@app.patch("/networking/interface/{name}/move/{namespace}", tags=["networking"])
def move_interface_to_namespace(name :str, namespace :str, current_user: User = Security(process_user_claim, scopes=["networking*"])) -> bool:
	"""
	This API endpoint can be used to move a certain interface into a namespace.
	This endpoint does not create the namespace however. Use `/networking/namespace/{name}`
	"""
	return bool(ip.link(f"set {name} netns {namespace}").exit_code == 0)