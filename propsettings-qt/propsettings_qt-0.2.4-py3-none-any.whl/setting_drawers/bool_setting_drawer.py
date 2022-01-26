from PySide2.QtWidgets import QCheckBox
from PySide2.QtCore import Qt

from propsettings.setting import Setting
from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer


class BoolSettingDrawer(SettingDrawer):
	"""
	SettingDrawer que se encarga de las configuraciones de tipo bool a través de un QCheckBox.
	"""

	def __init__(self, setting_owner, setting: Setting):
		super().__init__(setting_owner=setting_owner, setting=setting)
		# validar tipo de dato de la configuración (setting)
		st = self._setting_type
		if st != bool:
			raise TypeError(f'Wrong setting type: {st}. Setting must be of type bool.')

		self.checkbox = _CheckBoxHandler(bool_handler=self)
		self.checkbox.stateChanged.connect(self._on_state_changed)
		self._set_value_to_checkbox()

	def get_widget(self):
		return self.checkbox

	def _set_value_to_checkbox(self):
		value = self._get_value()
		self.checkbox.setChecked(value)

	def _on_state_changed(self, state):
		"""
		Evento ejecutado cuando el valor del checkbox es editado.
		:return:
		"""
		value = state == Qt.CheckState.Checked
		self._set_value(value)


class _CheckBoxHandler(QCheckBox):
	"""
	La única función de esta clase es ser un QCheckBox que tenga como miembro al BoolHandler para que este se quede
	en memoria.
	"""

	def __init__(self, bool_handler, parent=None):
		super().__init__(parent=parent)
		self.bool_handler = bool_handler
