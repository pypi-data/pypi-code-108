class NoDocumentError(Exception):
    '''
    statusCodeが107, 108, 111の時に発生するエラー
    '''
    pass


class ParameterError(Exception):
    '''
    statusCodeが204, 208, 212, 301, 400の時に発生するエラー
    '''
    pass


class TooManyAccessError(Exception):
    '''
    statusCodeが203の時に発生するエラー
    '''
    pass


class TemporaryError(Exception):
    '''
    statusCodeが210, 302, 303の時に発生するエラー
    '''
    pass


class UnknownError(Exception):
    '''
    statusCodeが999かその他定義されていないコードの時に発生するエラー
    '''
    pass




def is_error(response):
    message_format = "%s: %s"
    status_code = response['result']['statusCode']
    if status_code == "100":
        return

    error_message = response['result']['errorMessage']
    message = message_format % (status_code, error_message)

    if status_code == "203":
        raise TooManyAccessError(message)

    if status_code in {"210", "302", "303"}:
        raise TemporaryError(message)

    if status_code in {"107", "108", "111"}:
        raise NoDocumentError(message)

    if status_code in {"204", "208", "212", "301", "400"}:
        raise ParameterError(message)

    raise UnknownError(message)


def try_get(func, key, errors=(TooManyAccessError), func_when_error=None):
    try:
        info = func(key)
    except errors as e:
        if func_when_error is not None:
            return func_when_error(func, key, e)
        else:
            return None
    else:
        return info
