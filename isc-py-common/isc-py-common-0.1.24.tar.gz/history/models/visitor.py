import logging
from datetime import timedelta

from django.db.models import Manager, Model, CharField, DateTimeField, UniqueConstraint, Q, BigAutoField
from django.utils import timezone

from history import utils

logger = logging.getLogger(__name__)


class VisitorManager(Manager):

    def active(self, timeout=None):
        """
        Retrieves only visitors who have been active within the timeout
        period.
        """
        if not timeout:
            timeout = utils.get_timeout()

        now = timezone.now()
        cutoff = now - timedelta(minutes=timeout)

        return self.get_queryset().filter(last_update__gte=cutoff)


class Visitor(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    session_key = CharField(max_length=40)
    username = CharField(max_length=255, null=True, blank=True)
    ip_address = CharField(max_length=20)
    user_agent = CharField(max_length=255)
    referrer = CharField(max_length=255)
    url = CharField(max_length=255)
    session_start = DateTimeField()
    last_update = DateTimeField()
    objects = VisitorManager()

    def __str__(self):
        return u'{0} at {1} '.format(
            self.username,
            self.ip_address
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_start = timezone.now()
        self.last_update = timezone.now()

    @property
    def time_on_site(self):
        """
        Attempts to determine the amount of time a visitor has spent on the
        site based upon their information that's in the database.
        """
        if self.session_start:
            seconds = (self.last_update - self.session_start).seconds

            hours = seconds / 3600
            seconds -= hours * 3600
            minutes = seconds / 60
            seconds -= minutes * 60

            return u'%i:%02i:%02i' % (hours, minutes, seconds)
        else:
            return 'unknown'

    class Meta:
        verbose_name = 'Посетитель'
        ordering = ('-last_update',)
        unique_together = ('username', 'ip_address',)
        constraints = [
            UniqueConstraint(fields=['username', 'ip_address'], name='Visitor_unique_1'),
            UniqueConstraint(fields=['ip_address'], condition=Q(username=None), name='Visitor_unique_2'),
        ]
