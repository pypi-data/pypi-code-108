from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtWidgets import QLineEdit

from propsettings.setting import Setting
from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer


class TextSettingDrawer(SettingDrawer):
	"""
	SettingDrawer que se encarga de las configuraciones de tipo int, float y string a través de un QLineEdit.
	"""

	def __init__(self, setting_owner, setting: Setting):
		super().__init__(setting_owner=setting_owner, setting=setting)

		# validar tipo de dato de la configuración (setting)
		st = self._setting_type
		if st != int and st != float and st != str:
			raise TypeError(f'Wrong setting type: {st}. Setting must be of type string (str) or integer (int) or float (float).')

		self.edit = _LineEditHandler(text_handler=self)
		self.edit.editingFinished.connect(self._on_text_edited)
		self._validate_property_type()
		self._set_edit_from_value()

	def get_widget(self):
		return self.edit

	def _validate_property_type(self):
		"""
		Poner validadores al campo de edición para que solo acepte valores del tipo de dato de la propiedad.
		:return:
		"""
		if self._setting_type == int:
			self.edit.setValidator(QtGui.QIntValidator())
		elif self._setting_type == float:
			self.edit.setValidator(QtGui.QDoubleValidator())

	def _get_value_from_edit(self):
		"""
		Obtener valor a partir del string editado en el campo de edición
		:return:
		"""
		value = self.edit.text()
		if self._setting_type == int:
			value = int(value)
		elif self._setting_type == float:
			value = float(value)
		return value

	def _set_edit_from_value(self):
		"""
		Poner el valor de la propiedad en el QLineEdit (campo de edición)
		:return:
		"""
		value = self._get_value()
		self.edit.setText(str(value))

	@QtCore.Slot()
	def _on_text_edited(self):
		"""
		Evento ejecutado cuando el valor del campo de edición es editado.
		:return:
		"""
		value = self._get_value_from_edit()
		self._set_value(value)


class _LineEditHandler(QLineEdit):
	"""
	La única función de esta clase es ser un QLineEdit que tenga como miembro al TextHandler para que este se quede
	en memoria.
	"""

	def __init__(self, text_handler, parent=None):
		super().__init__(parent=parent)
		self.text_handler = text_handler
