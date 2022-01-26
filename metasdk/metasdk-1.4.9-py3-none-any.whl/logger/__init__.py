from __future__ import print_function
import atexit
import logging
import sys
import traceback

from fluent import handler
import metasdk

# http://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
# Отключаем логи от бибилиотеки requests
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

LOGGER_ENTITY = {}
REQUEST_LOG = {}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def create_logger(service_id=None, service_ns=None, build_num=None, gcloud_log_host_port=None, debug=True):
    if not service_id:
        service_id = 'unknown'

    # http://stackoverflow.com/questions/3220284/how-to-customize-the-time-format-for-python-logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    formatter = StdoutFormatter('%(asctime)s:%(levelname)s: %(message)s %(context)s', datefmt="%H:%M:%S")
    ch.setFormatter(formatter)

    root_logger.addHandler(ch)

    if not debug:
        gcloud_logs_parts = gcloud_log_host_port.split(':')
        if len(gcloud_logs_parts) != 2:
            raise ValueError("GCLOUD_LOG_HOST_PORT задан неправильно. Проверьте правильность написания HOST:PORT")

        service = service_ns + '.' + service_id
        h = handler.FluentHandler(service, host=gcloud_logs_parts[0], port=int(gcloud_logs_parts[1]))

        g_cloud_formatter = GCloudFormatter()
        g_cloud_formatter.service = service
        g_cloud_formatter.build_num = build_num
        h.setFormatter(g_cloud_formatter)

        root_logger.addHandler(h)

        def exit_handler():
            # Обязательно закрыть сокет по доке
            # https://github.com/fluent/fluent-logger-python
            h.close()

        atexit.register(exit_handler)


def prepare_errors(record):
    dict__ = record.__dict__

    dict__.setdefault('context', {})
    context = dict__.get('context')
    context.update(LOGGER_ENTITY)

    try:
        if record.levelno >= 40:
            if REQUEST_LOG:
                context["httpRequest"] = REQUEST_LOG
            # Ошибки и выше готовим для Google Cloud ErrorReporting
            # https://cloud.google.com/error-reporting/reference/rest/v1beta1/ErrorContext
            exc_type, exc_value, exc_tb = sys.exc_info()
            a = traceback.extract_tb(exc_tb)
            first_ex = a[-1]
            report_location = {'filePath': first_ex.filename, 'functionName': first_ex.name,
                               'lineNumber': first_ex.lineno}
            context.update({
                'reportLocation': report_location,
            })
    except Exception as ignore:
        pass

    ex = context.get("e")
    if ex:
        context.update({
            'e': {
                'message': str(ex),
                'trace': str(traceback.format_exc()),
            }}
        )
    return context


class GCloudFormatter(handler.FluentRecordFormatter, object):
    service = None
    build_num = None

    def format(self, record):
        # Create message dict
        context = record.context if hasattr(record, 'context') else {}
        context.update(metasdk.logger.LOGGER_ENTITY)
        context.update(prepare_errors(record))

        message = {
            "message": record.getMessage(),
            "severity": record.levelname,
            "serviceContext": {
                "service": self.service,
                "version": self.build_num
            }
        }
        if 'e' in context and isinstance(context['e'], dict) and 'trace' in context['e']:
            message['stack_trace'] = message['message'] + "\n" + context['e']['trace']
            # получение имени класса ошибки, автоматически добавляется entity
            message['error_class'] = message['message'].split()[-1]
            del context['e']['trace']
        message['context'] = context

        return message

    def formatException(self, record):
        """
        Format and return the specified exception information as a string.
        :type record logging.LogRecord
        :rtype: dict
        """
        if record.exc_info is None:
            return {}

        (exc_type, exc_message, trace) = record.exc_info

        return {
            'e': {
                'class': str(type(exc_type).__name__),  # ZeroDivisionError
                'message': str(exc_message),  # integer division or modulo by zero
                'trace': list(traceback.format_tb(trace)),
            }
        }


class StdoutFormatter(logging.Formatter, object):
    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        dict__ = record.__dict__
        dict__.setdefault('context', {})
        context = dict__.get('context')
        context.update(LOGGER_ENTITY)
        ex = context.get("e")
        if ex:
            context.update({'e': {
                'class': str(type(ex).__name__),
                'message': str(ex),
                'trace': str(traceback.format_exc()),
            }})
            eprint(str(ex) + "\n" + str(traceback.format_exc()))
        s = self._fmt % dict__
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            try:
                s = s + record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                s = s + record.exc_text.decode(sys.getfilesystemencoding(),
                                               'replace')
        return s
