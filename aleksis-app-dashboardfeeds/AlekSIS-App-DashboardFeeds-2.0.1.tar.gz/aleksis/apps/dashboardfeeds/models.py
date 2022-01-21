import datetime
import logging

from django.contrib import messages
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from feeds.models import Source

from aleksis.core.models import DashboardWidget

from .util.event_feed import get_current_events_with_cal

logger = logging.getLogger(__name__)


class RSSFeedWidget(DashboardWidget):
    template = "dashboardfeeds/rss.html"

    url = models.URLField(verbose_name=_("RSS feed source URL"))
    base_url = models.URLField(
        verbose_name=_("Base URL of related website"),
        help_text=_("The widget will have a link to visit a related website to read more news"),
    )
    text_only = models.BooleanField(
        verbose_name=_("Text only"),
        help_text=_("Do not show an image to depict the news item"),
        default=False,
    )

    rss_source = models.ForeignKey(Source, on_delete=models.CASCADE, editable=False, null=True)

    def save(self, *args, **kwargs):
        # Update the linked RSS source object to transfer data into django-feeds
        if not self.rss_source:
            self.rss_source = Source()
        self.rss_source.name = self.title
        self.rss_source.feed_url = self.url
        self.rss_source.site_url = self.base_url

        self.rss_source.last_success = datetime.datetime.utcnow()
        self.rss_source.last_change = datetime.datetime.utcnow()

        self.rss_source.live = self.active
        self.rss_source.save()

        super().save(*args, **kwargs)

    def get_context(self, request):
        posts = self.rss_source.posts.all().order_by("-created")
        post = posts[0] if len(posts) > 0 else None
        feed = {
            "title": self.title,
            "url": self.rss_source.feed_url,
            "base_url": self.rss_source.site_url,
            "base_image": self.rss_source.image_url,
            "result": post,
            "hide_image": self.text_only,
        }
        return feed

    class Meta:
        verbose_name = _("RSS Widget")
        verbose_name_plural = _("RSS Widgets")


@receiver(post_delete, sender=RSSFeedWidget)
def delete_rss_source_reverse(sender, **kwargs):
    try:
        if kwargs["instance"].rss_source:
            kwargs["instance"].rss_source.delete()
    except Source.DoesNotExist:  # Avoid endless looping
        pass


class ICalFeedWidget(DashboardWidget):
    template = "dashboardfeeds/ical.html"

    url = models.URLField(verbose_name=_("iCalendar URL"))
    base_url = models.URLField(
        verbose_name=_("Base URL of related calendar"),
        help_text=_("The widget will have a link to visit a related website to see more events"),
    )
    events_count = models.IntegerField(verbose_name=_("Number of displayed events"), default=5)

    def get_context(self, request):
        try:
            events = get_current_events_with_cal(self.url, self.events_count)
        except Exception as e:
            events = []
            logger.error(str(e))
            self.broken = True
            self.save()
            if request:
                messages.error(request, _("There was an error getting your calendar."))

        feed = {
            "base_url": self.base_url,
            "feed_events": events,
        }
        return feed

    class Meta:
        verbose_name = _("iCalendar Widget")
        verbose_name_plural = _("iCalendar Widgets")
