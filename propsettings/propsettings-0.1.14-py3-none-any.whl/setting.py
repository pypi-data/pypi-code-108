import copy
from typing import List

from propsettings.decorator import Decorator
from propsettings.setting_type import SettingType


class Setting(property):
	"""
	Propiedad (property) pensada principalmente para mostrarla en interfaces de usuario.
	"""
	def __init__(
			self,
			fget=None, fset=None, fdel=None, doc=None,
			label: str = None, sort_order: int = 0, setting_value_type: type = None,
			setting_type: SettingType = None, decorators: List[Decorator] = None):
		self._label = label
		self._sort_order = sort_order
		self._setting_value_type = setting_value_type
		self._setting_type = setting_type
		self._decorators = decorators
		property.__init__(self, fget=fget, fset=fset, fdel=fdel, doc=doc)

	@property
	def label(self) -> str:
		return self._label

	@property
	def sort_order(self):
		return self._sort_order

	@property
	def setting_value_type(self):
		return self._setting_value_type

	@property
	def setting_type(self) -> SettingType:
		return self._setting_type

	@property
	def decorators(self) -> List[Decorator]:
		return copy.copy(self._decorators)

	def __str__(self) -> str:
		return f'{self.label})'
