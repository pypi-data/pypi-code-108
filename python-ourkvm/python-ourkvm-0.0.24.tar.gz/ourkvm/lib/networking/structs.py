from typing import Union, Optional
from pydantic import BaseModel

class NamespaceStruct(BaseModel):
	from_: Union[bool, None, str]
	to: Union[bool, None, str]

	class Config:
		# https://github.com/samuelcolvin/pydantic/issues/153
		fields = {
			'from_': 'from'
		}

	def dict(self, *args, **kwargs): # type: ignore
		d = super().dict(*args, **kwargs)
		d['from'] = d.pop('from_')
		return d

class InterfaceStruct(BaseModel):
	"""
	The format of information found in ``config["interfaces"]`` for a VM .cfg file.
	"""
	name: str
	type: str
	namespace: Optional[NamespaceStruct] = None
	mac: Optional[Union[str, bool]] = None
	veth_pair: Optional[str] = None
	bridge: Optional[str] = None
	attach: bool = False