import inspect
from typing import Iterable, Type

import yaml

from propsettings.decorator import Decorator
from propsettings.setting import Setting
from propsettings.setting_type import SettingType


def _build_setting(member_name, label=None, sort_order=0, setting_value_type=None, setting_type=None, decorators=None):
	"""
	Construir un objeto de tipo Setting a partir del nombre de una variable miembro.
	:param member_name: nombre de la variable miembro.
	:param label: etiqueta de la variable que se mostrará en la UI.
	:param setting_type: tipo de dato de la variable.
	:return:
	"""
	# crear get
	def getter(instance):
		return instance.__getattribute__(member_name)

	# crear set
	def setter(instance, value):
		instance.__setattr__(member_name, value)

	capitalized = member_name.strip('_').capitalize().replace('_', ' ')
	label = label or capitalized
	stg = Setting(fget=getter, fset=setter, label=label, sort_order=sort_order,
				  setting_value_type=setting_value_type, setting_type=setting_type, decorators=decorators)
	return stg


def register_as_setting(
		clazz: type,
		member_name: str,
		label: str = None,
		sort_order: int = 0,
		setting_value_type: type = None,
		setting_type: Type[SettingType] = None,
		decorators: Type[Decorator] = None
):
	"""
	Registrar un miembro de una clase como parámetro configurable (Setting) de dicha clase.

	Ejemplo:

	class A:
		def __init__(self, a):
			self.a = a

	register_as_setting(A, 'a')

	:param decorators:
	:param setting_value_type:
	:param sort_order:
	:param clazz: clase a la que se desea añadir la propiedad. Si es una instancia entonces se obtiene su clase.
	:param member_name: nombre del miembro de la clase.
	:param label: [opcional] eqiqueta que identifica al parámetro configurable.
	Pensada para usarse en interfaces de usuario que muestren los parámetros configurables de un objeto.
	:param setting_type: [opcional] tipo de dato del parámetro.
	Es una manera de indicar cómo debe ser tratado este parámetro desde una interfaz de usuario.
	:return:
	"""
	if not inspect.isclass(clazz):
		clazz = type(clazz)

	stg = _build_setting(member_name, label, sort_order, setting_value_type, setting_type, decorators)
	stg_name = f"setting_{member_name}"
	setattr(clazz, stg_name, stg)


def get_settings_from_members(obj):
	"""
	TODO este método por ahora no hace falta. Considerar quitarlo.
	TODO validar que devuelva los Settings que ya tenga este objeto registrado y que no los duplique.
	Obtener lista de objetos Setting asociados a todos las variable públicas de un objeto.
	Nótese que estas Setting's no se añaden al objeto (ni a la clase del objeto) como miembros tal y como hace el
	método register_as_setting.
	:param obj:
	:return:
	"""
	settings = []
	for member_name, member in inspect.getmembers(obj):
		if not member_name.startswith('_'):
			settings.append(_build_setting(member_name))


def get_settings(obj) -> list:
	"""
	Obtener lista de propiedades de tipo Setting de un objeto.
	:param obj:
	:return:
	"""
	if inspect.isclass(obj):
		clazz = obj
	else:
		clazz = type(obj)
	settings = inspect.getmembers(clazz, lambda x: isinstance(x, Setting))
	return [stg for _, stg in settings]


def has_settings(obj):
	"""
	Dice si un objeto tiene settings.
	:param obj:
	:return:
	"""
	return len(get_settings(obj)) > 0


def get_dict_settings(obj):
	"""
	Diccionario con la etiqueta de las settings como llaves y los valores como valor. Si el valor no es un tipo de dato
	primitivo, entonces es un diccionario con las settings de ese objeto.
	:param obj:
	:return:
	"""
	dict_stg = {}
	settings = get_settings(obj)
	for stg in settings:
		key = stg.label
		value = stg.fget(obj)
		if isinstance(value, bool) or isinstance(value, int) or isinstance(value, float) or isinstance(value, str):
			dict_stg[key] = value
		elif isinstance(value, Iterable):
			pass  # TODO soporte para iterables
		else:
			class_name = type(value).__name__
			module_name = value.__module__
			value = get_dict_settings(value)
			key = f'{key}({module_name}.{class_name})'
			dict_stg[key] = value
			pass
	return dict_stg


def write_settings_to_yaml(output, obj):
	dict_settings = get_dict_settings(obj)
	file = open(output, 'w')
	yaml.dump(dict_settings, file, default_flow_style=False)
	file.close()


def read_yaml(pth):
	with open(pth) as f:
		d = yaml.load(f)
		print(d)
		print()


if __name__ == '__main__':
	class A:
		def __init__(self, a=1, s='a'):
			self.a = a
			self.s = s
	register_as_setting(A, 'a')
	register_as_setting(A, 's', 'Argument S')
	class B:
		def __init__(self, b=2):
			self.b = b
			self.stg = A(4, 'b')
	register_as_setting(B, 'b')
	register_as_setting(B, 'stg')
	b = B()
	write_settings_to_yaml('b.yaml', b)
