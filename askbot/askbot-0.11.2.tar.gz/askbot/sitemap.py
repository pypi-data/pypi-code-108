from django.contrib.sitemaps import Sitemap
from askbot.models import Post


class QuestionsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        questions = Post.objects.get_questions()
        questions = questions.exclude(deleted=True)
        questions = questions.exclude(approved=False)
        # this also references fields of another object, rather than just the
        # related object. Removing the field references, leaving only object
        # reference
        return questions.select_related('thread')

    def lastmod(self, obj):
        return obj.thread.last_activity_at

    def location(self, obj):
        return obj.get_absolute_url()
