from propsettings.setting import Setting
from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer


class ObjectSettingDrawer(SettingDrawer):
	"""
	SettingDrawer que se encarga de las configuraciones que sean de tipo object.
	Estas solo se podrán modificar si tienen miembros de tipo Setting o si son de algún tipo de dato que se puede cargar.
	"""

	def __init__(self, setting_owner, setting: Setting):
		from propsettings_qt.ui_settings_area import SettingsAreaWidget

		super().__init__(setting_owner=setting_owner, setting=setting)
		self.widget = SettingsAreaWidget()
		self.widget.populate_object(setting.fget(self._setting_owner))

	def get_widget(self):
		return self.widget

	def _on_configurable_object_selected(self, obj):
		"""
		Capturar evento de selección de objeto en combobox. Solo se usa cuando el objeto que se está configurando se
		puede cargar desde memoria externa y por tanto se puede seleccionar en un combobox.
		:param obj:
		:return:
		"""
		self._set_value(obj)

