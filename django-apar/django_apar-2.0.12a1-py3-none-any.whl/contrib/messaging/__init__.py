"""Initilize properties."""


class MessagingError(Exception):
    """Custom error type for the app."""
    pass


default_app_config = 'aparnik.contrib.messaging.apps.MessagingConfig'
