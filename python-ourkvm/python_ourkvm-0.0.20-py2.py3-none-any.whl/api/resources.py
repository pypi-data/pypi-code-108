import pathlib
import uuid
import shutil
from typing import Optional
from pydantic import BaseModel
from fastapi import Security, HTTPException
from .app import app
from .security import User, process_user_claim
from ..lib.qemu import qemu_img

class Resource(BaseModel):
	location: str = '/srv/qemu/harddrives/'
	friendly_name: str = 'Harddrive'
	drive_format: str = 'qcow2'
	drive_size: int = 20 # in GB
	unique_identifier: Optional[str] = None

@app.put("/resource/harddrive/{name}", tags=["resource"])
def create_virtual_harddrive(name :str, information :Resource, current_user: User = Security(process_user_claim, scopes=["resource*"])) -> Resource:
	"""
	This endpoint creates a virtual disk image using `qemu-img create`
	"""

	information.unique_identifier = str(uuid.uuid1())
	drive_path = pathlib.Path(information.location) / information.unique_identifier / f"{name}.{information.drive_format}"

	if not drive_path.exists():
		drive_path.parent.mkdir(parents=True, exist_ok=True)
		if (output := qemu_img(f"create -f {information.drive_format} {drive_path} {information.drive_size}G")).exit_code != 0:
			raise SystemError(f"Could not create image {drive_path}: {output}")

	return information

@app.delete("/resource/harddrive/{uuid}", tags=["resource"])
def delete_virtual_harddrive(uuid :str, information :Resource, current_user: User = Security(process_user_claim, scopes=["resource*"])) -> None:
	"""
	This endpoint deletes a virtual drive and all it's snapshots.
	"""

	drive_path = pathlib.Path(information.location) / uuid

	if not drive_path.exists():
		HTTPException(status_code=404, detail=f"Could not locate harddrive image {drive_path}")

	shutil.rmtree(str(drive_path), ignore_errors=True)