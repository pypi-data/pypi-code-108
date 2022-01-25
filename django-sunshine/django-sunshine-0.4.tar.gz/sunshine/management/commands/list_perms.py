# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

"""
Django command for listing all available permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'List all current permissions'

    def handle(self, *args, **options):
        for p in Permission.objects.all():
            self.stdout.write(str(p))
