from kfpubsub.utils import HandlerManager
from django.conf import settings


class Handler(HandlerManager):

    def __init__(self):
        super(Handler, self).__init__(
            getattr(settings, 'BASE_DIR', ''),
            getattr(settings, 'EVENT_HANDLERS_DIR_NAME', 'event_handlers') ,
            getattr(settings, 'HANDLER_FILES_PREFIX', 'handlers_')
        )
