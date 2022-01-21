
from django.core.management import BaseCommand
from askbot import models
from askbot.utils.console import ProgressBar
from askbot.conf import settings as askbot_settings
import sys

class Command(BaseCommand):
    def handle(self, **options):
        tags = models.Tag.objects.all()
        message = 'Searching for unused tags:'
        total = tags.count()
        tags = tags.iterator()
        deleted_tags = list()
        for tag in ProgressBar(tags, total, message):
            if not tag.threads.exists():
                #if any user subscribed for the tag and
                #the user is not blocked, skip deleting the tag
                marks = tag.user_selections.all()
                do_delete = True
                for mark in marks:
                    if not mark.user.is_blocked():
                        do_delete = False
                        break

                if do_delete:
                    deleted_tags.append(tag.name)
                    tag.delete()

        if deleted_tags:
            found_count = len(deleted_tags)
            if found_count == 1:
                print("Found an unused tag %s" % deleted_tags[0])
            else:
                sys.stdout.write("Found %d unused tags" % found_count)
                if found_count > 50:
                    print(", first 50 are:", end=' ')
                    print(', '.join(deleted_tags[:50]) + '.')
                else:
                    print(": " + ', '.join(deleted_tags) + '.')
            print("Deleted.")
        else:
            print("Did not find any.")
