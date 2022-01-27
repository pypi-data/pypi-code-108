import inspect
import sys


def get_module_classes(name_module: str) -> list:
    """ Возвращает список классов модуля """
    return [
        obj for name, obj in inspect.getmembers(sys.modules[name_module])
        if (
            inspect.isclass(obj) and
            inspect.getmodule(obj).__name__ == name_module and
            'debug' not in name
        )
    ]


def get_module_classes_inheritor(module_name: str, base_class) -> list:
    """ Возвращает список классов модуля - наследников заданного базового класса """
    classes = get_module_classes(module_name)
    return [obj for obj in classes if (base_class in inspect.getmro(obj))]


def get_class_by_name(module_name: str, class_name: str):
    """ Возвращает класс по его имени """
    return getattr(sys.modules[module_name], class_name)
