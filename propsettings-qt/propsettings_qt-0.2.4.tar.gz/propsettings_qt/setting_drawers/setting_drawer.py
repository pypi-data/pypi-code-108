from abc import ABC, abstractmethod

from propsettings.setting import Setting


class SettingDrawer(ABC):
	"""
	Clase abstracta para implementar widgets que gestionen la entrada para dar valores a atributos de tipo configurable.Setting.
	Cuando los widgets editen el valor de la configuración, deben notificarlo a través del atributo event_value_edited.
	Las clases que hereden de esta no deben ser el widget ellas mismas para evitar multiherencia.
	En cambio, deben devolver el objeto widget a través del método abstracto get_widget.
	"""

	@abstractmethod
	def get_widget(self):
		"""
		Obtener el widget que recibe la entrada del usuario.
		:return:
		"""
		pass

	def __init__(self, setting_owner, setting: Setting):
		"""
		Constructor que recibe el objeto que tiene la configuración y la configuración en sí.
		:param setting_owner: objeto que tiene la configuración. Es necesario para asignarle valor a su configuración
		cuando se edite la configuración en el widget.
		:param setting: configuración (Setting) del objeto
		"""
		self._setting_owner = setting_owner
		self._setting = setting
		self._setting_type = setting.setting_value_type or type(self._get_value())

	def _get_value(self):
		"""
		Obtener el valor del parámetro configurable.
		:return:
		"""
		return self._setting.fget(self._setting_owner)

	def _set_value(self, value):
		"""

		:param value:
		:return:
		"""
		self._setting.fset(self._setting_owner, value)
