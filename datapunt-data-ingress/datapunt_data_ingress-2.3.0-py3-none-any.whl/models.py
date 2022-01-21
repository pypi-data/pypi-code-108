import sys
import traceback

from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone

from ingress.querysets import FailedMessageQuerySet, MessageQuerySet


class Collection(models.Model):
    name = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=False,
        help_text=(
            "The end of the url and also the key with which it can be retrieved from "
            "the queue. For example, in the url /ingress/example, the string 'example' "
            "is the name of the collection."
        ),
    )
    ingress_enabled = models.BooleanField(default=True)
    consumer_enabled = models.BooleanField(default=False)

    @property
    def url_path(self):
        try:
            return reverse('ingress', kwargs={'collection_name': self.name})
        except NoReverseMatch:
            return None


class BaseMessage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, db_index=True)
    raw_data = models.TextField(
        help_text="To store raw received data to be consumed by a separate consumer"
    )
    consume_started_at = models.DateTimeField(null=True, db_index=True)
    consume_succeeded_at = models.DateTimeField(null=True, db_index=True)

    @property
    def consume_started(self):
        return self.consume_started_at is not None

    @property
    def consume_succeeded(self):
        return self.consume_succeeded_at is not None

    def set_consume_started(self, save_immediately=True):
        self.consume_started_at = timezone.now()
        if save_immediately:
            self.save()

    def set_consume_succeeded(self, save_immediately=True):
        self.consume_succeeded_at = timezone.now()
        if save_immediately:
            self.save()

    class Meta:
        abstract = True


class Message(BaseMessage):
    objects = MessageQuerySet.as_manager()

    def move_to_failed_queue(self):
        # In case consumption of the message fails
        # we move the message to a separate failed messages table
        stacktrace_str = "".join(traceback.format_exception(*sys.exc_info()))
        FailedMessage.objects.create(
            created_at=self.created_at,
            collection=self.collection,
            raw_data=self.raw_data,
            consume_started_at=self.consume_started_at,
            consume_succeeded_at=self.consume_succeeded_at,
            consume_failed_at=timezone.now(),
            consume_fail_info=stacktrace_str,
        )

        # remove the original message from the queue
        self.delete()


class FailedMessage(BaseMessage):
    """
    A message for which consumption failed
    """

    consume_failed_at = models.DateTimeField(null=True)
    consume_fail_info = models.TextField(
        null=True, help_text="To store stack traces or other info about the fail"
    )

    objects = FailedMessageQuerySet.as_manager()

    def move_to_ingress_queue(self):
        # In case we want to re-try consumption of the failed message
        # we move the message back to the ingress queue
        Message.objects.create(
            created_at=self.created_at,
            collection=self.collection,
            raw_data=self.raw_data,
            consume_started_at=None,
            consume_succeeded_at=None,
        )

        # remove the failed message from the queue
        self.delete()

    # @staticmethod
    # def move_to_ingress_queue_for_collection(collection_name):
    #     Start commit
    #     # Create all the new messages
    #     INSERT INTO message SELECT from
    #     # Delete all the failed messages
    #     FailedMessage.objects.filter().delete()
    #     end commit
