from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes import fields
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage as DjangoEmailMessage

# Create your models here.


class Notification(models.Model):
    Pending = 0
    SUCCESS = 1
    FAILED = 2

    PUSH_STATE_CHOICE = (
        (READY, _('Pending')),
        (SUCCESS, _('Success')),
        (FAILED, _('Failure')),
    )

    has_read = models.BooleanField(verbose_name=_('Read Or Not'), default=False)
    push_state = models.PositiveIntegerField(max_length=16, choices=PUSH_STATE_CHOICE, default=READY)
    to = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Receivers'))
    etag = models.TextField(verbose_name=_('Etag'), null=True, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Message Type"),
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("DingDingMessage", "WebsocketMessage", "EmailMessage")},
    )
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey()
    notified_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _("Notification")
        db_table = 'notification'


class Template(models.Model):
    """
    Message template
    """
    name = models.CharField(max_length=64, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    code = models.CharField(max_length=4, verbose_name=_("Template Code"), unique=True)
    title = models.CharField(max_length=64, verbose_name=_("Title"), null=True, blank=True)
    text = models.TextField(verbose_name=_("Template Text"))
    kwargs = models.JSONField(verbose_name=_("Kwargs"), null=True, blank=True)

    def __str__(self):
        return self.text

    def render(self, context):
        """
        Render message
        """
        try:
            return self.text.format(**context)
        except Exception:
            raise ValueError("Render message failed!")

    class Meta:
        verbose_name = _("Template")
        db_table = 'template'


class DingDingMessage(models.Model):
    """
    DingDing Message
    """
    TEXT = 'text'
    LINK = 'link'
    MARKDOWN = 'markdown'
    ACTION_CARD = 'actionCard'
    MESSAGE_TYPES = (
        (TEXT, "Text"),
        (LINK, "Link"),
        (MARKDOWN, "Markdown"),
        (ACTION_CARD, "ActionCard"),
    )

    title = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_("Content"))
    at_mobiles = models.JSONField(verbose_name=_('At Mobiles'), null=True, blank=True)
    msgtype = models.CharField(max_length=32, choices=MESSAGE_TYPES, default=MARKDOWN, verbose_name=_('Message Type'))
    is_at_all = models.BooleanField(default=False, verbose_name=_('At All'))
    extra = models.JSONField(verbose_name=_("API Kwargs"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    notify = GenericRelation(Notification)

    def to_message(self):
        content_key = 'content' if self.msgtype == self.TEXT else 'text'
        # TODO change json format depending on msgtype.
        if self.at_mobiles:
            format_at_str = ("@" + mobile for mobile in self.at_mobiles)
            content = ' '.join(format_at_str) + '\n\n' + self.content
        else:
            content = self.content
        return {
            "msgtype": self.msgtype,
            "at": {"atMobiles": self.at_mobiles, "isAtAll": self.is_at_all},
            self.msgtype: {"title": self.title, content_key: content, **(self.extra or {})},
        }

    class Meta:
        verbose_name = _("DingDing Message")
        db_table = 'dingding_message'


class WebsocketMessage(models.Model):
    """
    Websocket Message
    """
    DEFAULT_MESSAGE_TYPE = 'notify'

    title = models.CharField(max_length=64, null=True, blank=True, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    groups = models.JSONField(verbose_name=_('Receive Groups'))
    msgtype = models.CharField(max_length=32, verbose_name=_('Message Type'), default=DEFAULT_MESSAGE_TYPE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    notify = GenericRelation(Notification)

    def to_message(self):
        return {
            "type": 'notify.message',
            "msgtype": self.msgtype,
            "title": self.title,
            "message": self.content,
        }

    class Meta:
        verbose_name = _("Websocket Message")
        db_table = 'websocket_message'


class EmailMessage(models.Model):
    """
    Email Message
    """
    subject = models.CharField(max_length=128, verbose_name=_("Subject"))
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    sender = models.EmailField(verbose_name=_("Sender"), default=settings.DEFAULT_FROM_EMAIL)
    receivers = models.JSONField(verbose_name=_('Receivers'))
    cc = models.JSONField(null=True, blank=True, verbose_name=_("CC"))
    content_subtype = models.CharField(max_length=32, verbose_name=_("Content Subtype"), default="text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    notify = GenericRelation(Notification)

    def to_message(self):
        email = DjangoEmailMessage(self.subject, self.content, to=self.receivers, cc=self.cc)
        email.content_subtype = self.content_subtype
        return email

    class Meta:
        verbose_name = _("Email Message")
        db_table = 'email_message'
