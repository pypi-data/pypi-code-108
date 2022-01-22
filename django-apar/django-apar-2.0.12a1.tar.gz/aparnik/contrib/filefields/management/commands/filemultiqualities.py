# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

import subprocess
import os

from aparnik.contrib.filefields.models import FileField


class Command(BaseCommand):
    # Show this when the user types help
    help = "Generate multiple qualities File fields"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        queryset = FileField.objects.multi_quality()

        for file in queryset:
            # check file exist
            path = file.file_direct.path
            infile = path
            outfile = '%s%s'%(path, file.file_another_quality)

            if file.type == FileField.FILE_MOVIE:
                file.multi_quality_processing = 1
                if file.is_lock:
                    is_lock = file.is_lock
                    # unlock
                    file.is_lock = not is_lock
                    file.save()
                    file.is_lock = is_lock
                subprocess.call(
                    "ffmpeg -i '%s' -preset slow -codec:v libx264 -vf scale=-1:360 '%s'"%(path, outfile),
                    shell=True, close_fds=True
                )

            file.multi_quality_processing = 2
            if file.is_lock:
                is_lock = file.is_lock
                # unlock
                file.is_lock = not is_lock
                file.save()
                file.is_lock = is_lock
            file.save()

            # Finish and release lock
            # file.is_lock = False
            # file.save()

        finished_time = now()

        print(('multiple qualities done %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))
