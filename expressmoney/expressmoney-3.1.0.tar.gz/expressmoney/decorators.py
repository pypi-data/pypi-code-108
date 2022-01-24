from google.cloud import error_reporting

report = error_reporting.Client()


def report_exception(func):
    """Отправляет ошибку в Error Reporting вместо исключения"""
    def exception_wrapper(**kwargs):
        try:
            result = func(**kwargs)
            return result
        except Exception as exc:
            report.report(str(exc)[:2048])
    return exception_wrapper
