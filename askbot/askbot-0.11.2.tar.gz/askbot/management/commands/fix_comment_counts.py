"""Management command for fixing comment counts in questions and answers

Bug in converting answer to comment stored wrong comment count in target
question or answer, and in some cases that makes it imposible for users to view
all the comments.
"""

from django.core.management import BaseCommand
from django.db.models import signals, Count, F
from askbot.models import Post
from askbot.utils.console import ProgressBar

class Command(BaseCommand):

    help = "Fixes the wrong comment counts on questions and answers, "\
           "where answers have been converted to comments.\n"

    def remove_save_signals(self):
        """Prevent possible unvanted side effects of saving
        """
        signals.pre_save.receivers = []
        signals.post_save.receivers = []

    def handle(self, *arguments, **options):
        """Function that handles the command job
        """
        self.remove_save_signals()
        posts = Post.objects.annotate(real_comment_count=Count('comments')
                ).exclude(real_comment_count=F('comment_count'))
        count = posts.count()
        message = 'Fixing comment counts'
        for post in ProgressBar(posts.iterator(), count, message):
            new_count = post.comments.count();
            Post.objects.filter(id=post.id).update(comment_count=new_count)
