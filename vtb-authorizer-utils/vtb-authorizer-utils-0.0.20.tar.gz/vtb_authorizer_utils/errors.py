from typing import Optional, FrozenSet


class SchemaBuilderError(Exception):
    """ Ошибка при построении схемы правил сервиса """


class ServiceImportError(Exception):
    """ Ошибка импорта сервиса """


class NotInHierarchyError(Exception):
    """ Не найден в иерархии """


class NotAllowedParameterError(Exception):
    """
    Параметр запроса не разрешен
    """

    def __init__(self, not_allowed_parameters: FrozenSet[str],
                 allowed_parameters: Optional[FrozenSet[str]] = frozenset({})):
        self.message = f'Parameters "{",".join(not_allowed_parameters)}" are not allowed. List of allowed parameters: "{",".join(allowed_parameters)}"'
        super().__init__(self.message)
