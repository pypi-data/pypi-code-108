
from django.apps import apps

from modeltranslation.translator import translator

from articles import config
from articles.models import Article


translator.register(Article, fields=['title', 'description', 'text'])

if config.ARE_TAGS_ENABLED:
    translator.register(
        apps.get_model('articles', 'ArticleTag'),
        fields=['text'])

if config.IS_ARTICLE_TYPE_ENABLED:
    translator.register(
        apps.get_model('articles', 'ArticleType'),
        fields=['name'])
