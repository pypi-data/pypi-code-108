# noqa

from django.contrib import admin

from .models import DashboardWidget, ICalFeedWidget, RSSFeedWidget

admin.site.register(DashboardWidget)
admin.site.register(RSSFeedWidget)
admin.site.register(ICalFeedWidget)
