import requests
import warnings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.transaction import atomic
from asgiref.sync import async_to_sync
import channels.layers
import logging
from .models import (
    DingDingMessage,
    Notification,
    EmailMessage,
    WebsocketMessage,
    Template,
)
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


DEFAULT_COALESCE_TIME = 60


class NotificationBackend:
    notification_class = Notification
    template_class = Template
    message_class = None
    default_title = "Notification"

    # def __init__(self, *args, **kwargs):
    #     try:
    #         self.notification_settting = settings.DJANGO_NOTIFICATION
    #     except AttributeError:
    #         raise ImproperlyConfigured(f"'DJANGO_NOTIFICATION' must be set in settings.py")
    #
    #     self.notification_settting =

    def process_notification(self, instance, **kwargs):
        ...

    def process_message(self, message, receivers, title, **kwargs):
        ...

    def on_failure(self, message, notification, exc):
        notification.push_state = notification.FAILED
        notification.save(update_fields=("push_state",))

    def on_success(self, message, notification):
        notification.push_state = notification.SUCCESS
        notification.save(update_fields=("push_state",))

    @staticmethod
    def get_valid_kwargs(model, kwargs):
        if kwargs is None:
            return {}

        fields = [f.name for f in model._meta.get_fields()]
        return {k: v for k, v in kwargs.items() if k in fields}

    @atomic
    def perform_save(self, content, receivers, title, message_kwargs, notify_kwargs):
        """
        Process message
        """
        message = self.message_class(
            content=content, **self.get_valid_kwargs(self.message_class, message_kwargs)
        )
        self.process_message(message, receivers, title, **(message_kwargs or {}))
        message.save()
        notification = self.notification_class(
            content_object=message,
            **self.get_valid_kwargs(self.notification_class, notify_kwargs),
        )
        self.process_notification(notification, **(notify_kwargs or {}))
        notification.save()
        notification.to.set(receivers)
        return message, notification

    def send_with_template(self, receivers, context, template, title=None, **kwargs):
        content = template.render(context)
        return self.send(receivers, content, title=title, **kwargs)

    def send_message(self, instance, **kwargs):
        raise NotImplementedError

    def send(
        self,
        receivers,
        content,
        title=None,
        allow_resend=False,
        message_kwargs=None,
        notify_kwargs=None,
        **kwargs,
    ):
        """
        For details, see: https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
        """
        etag = notify_kwargs and notify_kwargs.get("etag")
        if etag and not allow_resend:
            if self.notification_class.objects.filter(etag=etag).exists():
                logger.info("重复消息！")
                return

        instance, notification = self.perform_save(
            content,
            receivers,
            title,
            message_kwargs=message_kwargs,
            notify_kwargs=notify_kwargs,
        )
        try:
            self.send_message(instance, **kwargs)
        except Exception as exc:
            self.on_failure(instance, notification, exc)
        else:
            self.on_success(instance, notification)

    def list(self):
        """
        Return notication queryset
        """
        return self.notification_class.objects.all()

    def clear(self):
        """
        Clear notification
        """
        self.notification_class.objects.delete()
        self.message_class.objects.delete()


class DingDingBotNotificationBackend(NotificationBackend):
    """
    A backend handle dingding message.
    """

    default_phone_field = "phone"
    message_class = DingDingMessage

    def __init__(self, webhook=None, user_phone_field=None, **kwargs):
        self.webhook = webhook or getattr(settings, "NOTIFICATION_DINGDING_WEBHOOK", None)
        if self.webhook is None:
            raise ImproperlyConfigured(f"'NOTIFICATION_DINGDING_WEBHOOK' must be set in settings.py")

        self.user_phone_field = user_phone_field or self.default_phone_field
        self.session = requests.Session()

    def process_message(self, message, receivers, title, **kwargs):
        try:
            message.title = title or self.default_title
            if not message.at_mobiles:
                message.at_mobiles = [
                    str(getattr(r, self.user_phone_field)) for r in receivers
                ]
        except AttributeError:
            pass

    def send_message(self, instance, **kwargs):
        """
        For details, see: https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
        """
        message = instance.to_message()
        resp = self.session.post(self.webhook, json=message)
        assert resp.json()["errcode"] == 0, resp.json()["errmsg"]


class EmailNotificationBackend(NotificationBackend):
    """
    A backend handle email message
    """

    message_class = EmailMessage

    def process_message(self, message, receivers, title, **kwargs):
        message.receivers = [r.email for r in receivers]
        message.subject = title or self.default_title

    def send_message(self, instance, **kwargs):
        """
        For details, see: ...
        """
        message = instance.to_message()
        message.send()


class WebsocketNotificationBackend(NotificationBackend):
    """
    A backend handle websocket message.
    """

    group_prefix = "notify"
    message_class = WebsocketMessage

    def get_group_name(self, user):
        return f"{self.group_prefix}-{user.pk}"

    def process_message(self, message, receivers, title, **kwargs):
        message.groups = [self.get_group_name(r) for r in receivers]
        message.title = title

    def send_message(self, instance, **kwargs):
        """
        For details, see: https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
        """
        message = instance.to_message()
        channel_layer = channels.layers.get_channel_layer()
        for group_name in instance.groups:
            async_to_sync(channel_layer.group_send)(group_name, message)


def notify(
    receivers,
    message=None,
    title=None,
    template_code=None,
    context=None,
    backends=None,
    allow_resend=True,
    save=False,
    message_coalesce=False,
    message_kwargs=None,
    notify_kwargs=None,
    **kwargs,
):
    try:
        backends = backends or settings.NOTIFICATION_BACKENDS
    except AttributeError:
        raise ImproperlyConfigured(
            "You must set NOTIFICATION_BACKENDS in 'settings.py'"
        )

    if message is None and not all([template_code, context]):
        raise ValueError("You must provide message or template.")

    if allow_resend is False:
        save = True

    for backend_cls in backends:
        if isinstance(backend_cls, str):
            backend_cls = import_string(backend_cls)

        if message:
            backend = backend_cls(**kwargs)
            backend.send(
                receivers,
                message,
                title=title,
                allow_resend=allow_resend,
                message_kwargs=message_kwargs,
                notify_kwargs=notify_kwargs,
                **kwargs,
            )
        else:
            try:
                template = backend_cls.template_class.objects.get(code=template_code)
            except ObjectDoesNotExist:
                raise ValueError(f"Template: {template_code} doesn't exist.")
            # `kwargs` is prior to `kwargs` defined in template
            title = title or template.title
            if template.kwargs and isinstance(template.kwargs, dict):
                default_kwargs = template.kwargs
                default_kwargs.update(kwargs)
            else:
                default_kwargs = kwargs

            backend = backend_cls(**default_kwargs)

            if message_coalesce and not isinstance(
                backend, DingDingBotNotificationBackend
            ):
                warnings.warn(
                    "`message_coalesce` is ignored, as it is now only supported by `DingDingBotNotificationBackend`.",
                    stacklevel=2,
                )
                message_coalesce = False

            backend.send_with_template(
                receivers,
                context,
                template,
                title=title,
                allow_resend=allow_resend,
                save=save,
                message_coalesce=message_coalesce,
                message_kwargs=message_kwargs,
                notify_kwargs=notify_kwargs,
                **default_kwargs,
            )


def notify_by_dingding(
    receivers,
    message=None,
    context=None,
    template_code=None,
    at_mobiles=None,
    msgtype="markdown",
    is_at_all=False,
    extra=None,
    allow_resend=True,
    save=False,
    message_coalesce=False,
    notify_kwargs=None,
    **kwargs,
):
    """
    Shortcut for dingding notification
    """
    backend_cls = DingDingBotNotificationBackend
    message_kwargs = dict(
        at_mobiles=at_mobiles, msgtype=msgtype, is_at_all=is_at_all, extra=extra
    )
    return notify(
        receivers,
        message=message,
        context=context,
        template_code=template_code,
        backends=(backend_cls,),
        allow_resend=allow_resend,
        save=save,
        message_coalesce=message_coalesce,
        message_kwargs=message_kwargs,
        notify_kwargs=notify_kwargs,
        **kwargs,
    )


def notify_by_email(
    receivers,
    message=None,
    context=None,
    template_code=None,
    cc=None,
    content_subtype="text",
    allow_resend=True,
    save=False,
    notify_kwargs=None,
    **kwargs,
):
    """
    Shortcut for email notification
    """
    backend_cls = EmailNotificationBackend
    message_kwargs = dict(cc=cc, content_subtype=content_subtype)
    return notify(
        receivers,
        message=message,
        context=context,
        template_code=template_code,
        backends=(backend_cls,),
        allow_resend=allow_resend,
        save=save,
        message_kwargs=message_kwargs,
        notify_kwargs=notify_kwargs,
        **kwargs,
    )


def notify_by_websocket(
    receivers,
    message=None,
    context=None,
    template_code=None,
    msgtype=None,
    allow_resend=True,
    save=False,
    notify_kwargs=None,
    **kwargs,
):
    """
    Shortcut for websocket notification
    """
    backend_cls = WebsocketNotificationBackend
    message_kwargs = {}
    if msgtype:
        message_kwargs.update(msgtype=msgtype)

    return notify(
        receivers,
        message=message,
        context=context,
        template_code=template_code,
        backends=(backend_cls,),
        allow_resend=allow_resend,
        save=save,
        message_kwargs=message_kwargs,
        notify_kwargs=notify_kwargs,
        **kwargs,
    )
