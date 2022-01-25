from modeltranslation.translator import TranslationOptions, translator

from notifications.models import Notification


class NotificationTranslationOptions(TranslationOptions):
    fields = ('name', 'message')


translator.register(Notification, NotificationTranslationOptions)
