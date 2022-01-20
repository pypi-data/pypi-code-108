from __future__ import annotations
from typing import Sequence, Union, Any

# Wrapper on top of callback names. This is to reduce overhead of checking if a metric name is tuple or string, since it
#  can be both, depending on context. Graph metrics are stored as a tuple of strings.
class CallbackName:
	def __init__(self, name:Union[str, CallbackName, Sequence[str]]):
		if isinstance(name, CallbackName):
			name = name.name #type: ignore
		if isinstance(name, str):
			name = (name, ) #type: ignore
		self.name:Sequence[str] = name #type: ignore

	def __str__(self) -> str:
		Str = []
		for i in range(len(self.name)):
			Str.append(str(self.name[i]))
		return "|".join(Str)

	def __repr__(self) -> str:
		return str(self)

	def __lt__(self, other:CallbackName) -> bool:  #type: ignore[override]
		if not isinstance(other, CallbackName):
			other = CallbackName(other) #type: ignore

		try: #type: ignore
			return self.name < other.name #type: ignore
		except Exception:
			breakpoint()
		return False

	def __eq__(self, other:CallbackName) -> bool: # type: ignore[override]
		if not isinstance(other, CallbackName):
			other = CallbackName(other) #type: ignore

		try:
			return self.name == other.name #type: ignore
		except Exception:
			breakpoint()
		return False

	def __hash__(self) -> int:
		return hash(self.name)