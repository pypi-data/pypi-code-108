from django.contrib import admin

# Register your models here.
from social_layer.notifications.models import *

admin.site.register(Notification)
