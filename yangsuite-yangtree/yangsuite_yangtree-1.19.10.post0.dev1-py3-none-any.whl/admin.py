# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.contrib import admin
from .models import YangSetTree


class YangSetTreeAdmin(admin.ModelAdmin):
    """Admin interface for YangSetTree table
    """
    list_display = ('set_id', 'setname', 'user', 'ref',
                    'plugin_name', 'repository',
                    'created_on', 'yangsettree_mtime')


admin.site.register(YangSetTree, YangSetTreeAdmin)
