# Copyright 2016 - 2021, Cisco Systems, Inc., all rights reserved.
import pytz

from django.db import models
from django.contrib.auth.models import User


def convert_datetime(dateobj, to_tz):
    try:
        tz = pytz.timezone(to_tz)
        return dateobj.astimezone(tz)
    except Exception:
        return dateobj


def format_date(dateobj, tz=None):
    if not dateobj:
        return ''
    dt = convert_datetime(dateobj, tz) if tz else dateobj
    return dt.strftime("%b %d %Y %I:%M:%S %p %Z")


class YangSetTree(models.Model):
    """Save the data while creating new YANGSet.
    """
    set_id = models.AutoField(primary_key=True)
    setname = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref = models.CharField(max_length=255, null=True, blank=True)
    plugin_name = models.CharField(max_length=100)
    set_modules = models.TextField(default="", null=True, blank=True)
    data = models.TextField(default="", null=True, blank=True)
    repository = models.CharField(max_length=255, null=True, blank=True)
    yangsettree_mtime = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.setname

    def __unicode__(self):
        return "YANG Set tree {0} for {1}. ".format(self.setname, self.user)
