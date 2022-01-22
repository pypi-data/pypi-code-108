"""admin.py file."""

from django.contrib import admin

from .models import Messaging


admin.site.register(Messaging)
