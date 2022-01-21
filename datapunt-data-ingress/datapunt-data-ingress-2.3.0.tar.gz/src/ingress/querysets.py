from django.db import models


class MessageQuerySet(models.QuerySet):
    def for_collection(self, collection):
        return self.filter(collection=collection)

    def not_consumed(self):
        return self.filter(consume_started_at__isnull=True)

    def consumed(self):
        return self.filter(consume_succeeded_at__isnull=False)


class FailedMessageQuerySet(MessageQuerySet):
    pass
