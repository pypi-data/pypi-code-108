
from django.apps import apps
from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def get_latest_articles(context, article_type=None, count=5):
    queryset = apps.get_model('articles', 'Article').objects.all()

    if article_type:
        queryset = queryset.filter(type__slug=article_type)

    return queryset[:count]


@register.simple_tag(takes_context=True)
def get_most_popular_articles(context, article_type=None, count=5):
    return apps.get_model('articles', 'Article').most_popular(
        article_type)[:count]
