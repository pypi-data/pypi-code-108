from metasdk.exceptions import AuthError, ServerError, RequestError, UnexpectedError, NoContentError


def get_api_call_headers(app):
    """
    Генерирует заголовки для API запроса.
    Тут же подкладывается авторизация

    :type app: metasdk.MetaApp
    """
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "User-Agent": app.user_agent,
    }
    if not app.developer_settings:
        raise AuthError({"message": "Для корректной работы SDK нужно установить настройки разработчика", "url": "https://apps.devision.io/page?a=63&p=3975"})
    headers.update(app.developer_settings.get('api_headers'))
    return headers


def process_meta_api_error_code(status_code, request, response_text):
    if status_code == 204:
        raise NoContentError(request)
    elif status_code == 401:
        raise AuthError(request)
    elif status_code >= 500:
        raise ServerError(response_text)
    elif status_code >= 400:
        raise RequestError(response_text)
    else:
        raise UnexpectedError(request)
