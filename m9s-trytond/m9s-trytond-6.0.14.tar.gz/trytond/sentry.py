# encoding: utf-8
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from werkzeug.exceptions import HTTPException

from trytond.config import config
from trytond.exceptions import TrytonException, UserError

logger = logging.getLogger(__name__)

sentry_dsn = config.get('sentry', 'dsn')
sentry_organisation = config.get('sentry', 'organisation', default='')
sentry_default_pii = config.getboolean('sentry', 'default_pii', default=False)
sentry_lang = config.get('sentry', 'lang', default='en')

ERROR_MESSAGE = {
    'ca': ("S'ha produït un error executant la vostra petició. S'ha "
        "enviat la informació a l'equip de {organisation} i ho resoldrem.\n\n"
        "Tot i amb això, si vols parlar-ne amb algú del nostre equip pots "
        "utilitzar la següent referència: {event}."),
    'es': ('Se ha producido un error ejecutando vuestra petición. Se ha '
        'enviado la información al equipo de {organisation} y lo resolveremos.\n\n'
        'A pesar de esto, si quieres hablar sobre la incidencia con alguien de '
        'nuestro equipo puedes utilizar la referencia siguiente: {event}.'),
    'en': ('There was an error while executing your request. We will check '
        'to see what could be the cause.\n\nHowever, if you want to talk to a '
        '{organisation} consultant about this issue, you may use the following '
        'reference: {event}'),
    'de': ('Bei der Ausführung Ihrer Anfrage ist ein Fehler aufgetreten. '
        'Die Information wurde an das Team von {organisation} gesendet, wir '
        'werden uns um die Behebung des Fehlers kümmern.\n\n'
        'Falls Sie mit einem unserer Mitarbeiter sprechen wollen, können Sie '
        'sich auf den folgenden Referenzcode beziehen: {event}'),
    }


def sentry_wrap(func):

    def wrap(*args, **kwargs):
        with sentry_sdk.push_scope() as scope:
            #scope.set_extra('debug', True)
            try:
                return func(*args, **kwargs)
            except (TrytonException, HTTPException):
                raise
            except Exception as e:
                sentry_sdk.capture_exception(e)
                event_id = sentry_sdk.last_event_id()[:6]
                language = sentry_lang
                if language not in ERROR_MESSAGE:
                    language = 'en'
                raise UserError(ERROR_MESSAGE[language].format(
                        organisation=sentry_organisation,
                        event=event_id))

    if sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(sentry_dsn, send_default_pii=sentry_default_pii)
        return wrap
    else:
        return func
