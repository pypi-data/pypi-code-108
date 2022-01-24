import io
import sys
import os

from cloudpickle import CloudPickler
from ipystate.serialization import Pickler, Unpickler
TAAS_ATTR = '_taas_registered_field'


def get_worker_info():
	from torch.utils.data._utils.worker import WorkerInfo
	worker_id = int(os.environ["RANK"])
	num_workers = int(os.environ["WORLD_SIZE"])
	return WorkerInfo(id=worker_id, num_workers=num_workers)


def register(data_loader):
	if not hasattr(data_loader, "__iter__"):
		raise ValueError(f"{data_loader} is not iterable")
	if hasattr(data_loader, TAAS_ATTR):
		raise ValueError(f"{data_loader} is already registered")
	try:
		output = io.BytesIO()
		Pickler(globals(), CloudPickler.dispatch_table, output, protocol=4).dump(data_loader)
		Unpickler(globals(), io.BytesIO(output.getvalue())).load()
	except NotImplementedError:
		raise ValueError(f"{data_loader} cannot be serialized")
	setattr(data_loader, TAAS_ATTR, True)


def unregistered(data_loader):
	if not hasattr(data_loader, TAAS_ATTR):
		raise ValueError(f"Dataloader {data_loader} is not registered")
	delattr(data_loader, TAAS_ATTR)


def is_registered(data_loader) -> bool:
	return hasattr(data_loader, TAAS_ATTR)


def get_registered_data_loaders_names() -> [str]:
	names = []
	for name, obj in vars(sys.modules["__main__"]).items():
		if is_registered(obj):
			names.append(name)
	return names
