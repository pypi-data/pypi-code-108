from django.core.management import BaseCommand
from django.db import transaction
from askbot.models import Post
from askbot.utils.console import ProgressBar

class Command(BaseCommand):
    help = 'Generates snippets for all posts'

    def handle(self, *args, **kwargs):
        posts = Post.objects.all()
        count = posts.count()
        message = 'Building post snippets'
        for post in ProgressBar(posts.iterator(), count, message):
            if hasattr(post, 'summary'):
                post.html = post.parse_post_text()['html']
                post.summary = post.get_snippet()
                post.save()
                transaction.commit()
                if post.thread:
                    post.thread.clear_cached_data()
        transaction.commit()
