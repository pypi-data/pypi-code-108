"""
API делится на 3 типа на основе ролевой модели:

- internal - используется для межсервисного взаимодействия только через системные учетные записи(СУЗ). Вызовы под СУЗ
  пользователей запрещены. Контекст не проверяется.
- admin - предназначен для доступов вне контекста. Это например, конструктор продуктов. Для него доступы выделяются
  независимо от оргструктуры и подразумевается ролевая модель без учёта контекста. Отличие от internal в том, что в этот
  тип API можно вызвать под пользовательским токеном.
- public - пользователи, сервисные аккаунты(в том числе пользовательские). Если есть контекст в URL, то он будет
  проверяться на наличие доступа.
"""
from typing import Set, Optional, Dict, Tuple

from vtb_authorizer_utils.authorizer_schema_builder import ContextType, AuthorizerSchemaBuilder


def authorizer_resource_type(service: str,
                             name: str,
                             title: Optional[str] = None,
                             description: Optional[str] = None,
                             base_url_pattern: Optional[str] = None,
                             default_context_types: Optional[Set[ContextType]] = None,
                             default_access_type: Optional[str] = 'public',
                             url_pattern_postfix: Optional[str] = '/'):
    """
    Добавление описания ресурсного типа. Декоратор, который применяется к классу, реализующего методы REST API
    :param service: имя сервиса, к которому будут привязаны правила
    :param name: имя ресурсного типа
    :param title: наименование
    :param description: описание
    :param base_url_pattern: базовый URL, если указан, то происходит дополнительная регистрация стандартных REST методов
    :param default_context_types: контексты доступа, которые указывается у стандартных REST методов.
    Доступные варианты - перечисление ContextType
    :param default_access_type: тип доступа, который указывается у стандартных REST методов, по умолчанию 'public'
    :param url_pattern_postfix: постфикс базового URL, по умолчанию '/'
    :return:
    """

    def decorator(view_class):
        if base_url_pattern:
            register_default_authorizer_resource_rules(view_class, base_url_pattern,
                                                       default_context_types=default_context_types,
                                                       default_access_type=default_access_type,
                                                       url_pattern_postfix=url_pattern_postfix)

        AuthorizerSchemaBuilder().add_resource_type(service, name, view_class.__qualname__, title, description)
        return view_class

    return decorator


def authorizer_resource_rule(http_method: str,
                             url_pattern: str,
                             access_type: str,
                             operation_name: str,
                             action_code: Optional[str] = None,
                             context_types: Optional[Set[ContextType]] = None, ):
    """
    Добавление описания ресурсного правила. Декоратор, который применяется к методу классу, реализующего метод REST API
    :param http_method: HTTP метод: get, post, put, patch, delete
    :param url_pattern: шаблон URL, например, /api/v1/{context_type}/{id}/tags/*/, где
    {context_type} - в случае указания контекста в context_types, параметр будет заменен на 'organizations', 'folders'
    или 'projects'. Будет создано столько правил, сколько указано контекстов в параметре context_types
    {id} - служебный параметр, который обрабатывается авторайзером
    * - указывает, что в этом месте может быть любое значение, например идентификатор сущности
    :param access_type: тип доступа. Возможные варианты internal, admin, public
    :param operation_name: имя операции
    :param action_code: уникальный код действия, который используется для заполнения поля "ДЕЙСТВИЯ" у сервиса
    :param context_types: контексты доступа. Доступные варианты - перечисление ContextType
    :return:
    """

    def decorator(view_method):

        if not action_code:
            method_name = str(view_method.__name__).lower()
            code = method_name
        else:
            code = action_code

        AuthorizerSchemaBuilder().add_resource_rule(http_method.upper(), url_pattern,
                                                    code, access_type, operation_name,
                                                    view_method.__qualname__,
                                                    context_types=context_types, )
        # У декоратора имеется приоритет
        view_method.skip = True

        return view_method

    return decorator


def register_default_authorizer_resource_rules(view_class,
                                               base_url_pattern: str,
                                               default_context_types: Optional[Set[ContextType]] = None,
                                               default_access_type: Optional[str] = 'public',
                                               url_pattern_postfix: Optional[str] = '/',
                                               detail_id_str: Optional[str] = '*'):
    """ Регистрация стандартных REST методов """

    methods = _create_methods(base_url_pattern, detail_id_str, url_pattern_postfix=url_pattern_postfix)
    _register_default_http_methods(view_class, methods, default_context_types, default_access_type)
    _register_default_actions(view_class, base_url_pattern, methods, detail_id_str,
                              default_context_types=default_context_types,
                              default_access_type=default_access_type,
                              url_pattern_postfix=url_pattern_postfix)


def _create_methods(base_url_pattern: str,
                    detail_id_str: str,
                    url_pattern_postfix: Optional[str] = '/') -> Dict[str, Tuple[str, str]]:
    api_view_url = _join_url(base_url_pattern, postfix=None, prefix=None)
    list_url = _join_url(base_url_pattern, postfix=url_pattern_postfix)
    detail_url = _join_url(base_url_pattern, detail_id_str, postfix=url_pattern_postfix)
    methods = {
        'get': ('get', api_view_url),
        'post': ('post', api_view_url),
        'put': ('put', api_view_url),
        'patch': ('patch', api_view_url),
        'delete': ('delete', api_view_url),

        'create': ('post', list_url),
        'retrieve': ('get', detail_url),
        'update': ('put', detail_url),
        'partial_update': ('patch', detail_url),
        'list': ('get', list_url),
        'destroy': ('delete', detail_url),
    }
    return methods


def _register_default_http_methods(view_class,
                                   methods: Dict[str, Tuple[str, str]],
                                   default_context_types: Optional[Set[ContextType]] = None,
                                   default_access_type: Optional[str] = 'public'):
    class_name = view_class.__name__

    for method, info in methods.items():
        if hasattr(view_class, method):
            view_method = getattr(view_class, method)
            if _skip(view_method):
                continue

            if callable(view_method):
                method_name = str(view_method.__qualname__)
                name = method_name if method_name.startswith(class_name) else f'{class_name}.{method_name}'
                operation_name = f'{method} in {class_name}'
                http_method = info[0]
                AuthorizerSchemaBuilder().add_resource_rule(http_method.upper(), info[1], method,
                                                            default_access_type,
                                                            operation_name, name,
                                                            context_types=default_context_types)


def _register_default_actions(view_class,  # pylint: disable=too-many-locals
                              base_url_pattern: str,
                              methods: Dict[str, Tuple[str, str]],
                              detail_id_str: str,
                              default_context_types: Optional[Set[ContextType]] = None,
                              default_access_type: Optional[str] = 'public',
                              url_pattern_postfix: Optional[str] = '/'):
    view_methods = [method for method in dir(view_class) if
                    not method.startswith('__') and not method.startswith('_') and method not in methods.keys()]
    for view_method_name in view_methods:
        view_method = getattr(view_class, view_method_name)
        if _skip(view_method):
            continue

        if hasattr(view_method, 'mapping') and hasattr(view_method, 'detail'):
            url_path = getattr(view_method, 'url_path')
            detail = getattr(view_method, 'detail')

            mapping = getattr(view_method, 'mapping')
            url_parts = (base_url_pattern, detail_id_str, url_path) if detail else (base_url_pattern, url_path)
            url = _join_url(*url_parts, postfix=url_pattern_postfix)
            for http_method, method in mapping.items():
                operation_name = f'{method} in {view_class.__name__}'

                AuthorizerSchemaBuilder().add_resource_rule(http_method.upper(), url, method,
                                                            default_access_type, operation_name,
                                                            f'{view_class.__qualname__}.{view_method.__name__}',
                                                            context_types=default_context_types)


def _skip(view_method) -> bool:
    if hasattr(view_method, 'skip'):
        skip = getattr(view_method, 'skip')
        return bool(skip)

    return False


def _join_url(*args, sep: Optional[str] = '/', prefix: Optional[str] = '/', postfix: Optional[str] = '/') -> str:
    if not args:
        return ''

    url = sep.join(arg.strip(sep) for arg in args) if len(args) > 1 else str(args[0]).lstrip(prefix).rstrip(postfix)
    if prefix:
        url = f'{prefix}{url}'
    if postfix:
        url = f'{url}{postfix}'
    return url
