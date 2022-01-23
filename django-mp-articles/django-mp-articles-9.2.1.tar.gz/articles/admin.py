
from django.apps import apps
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from modeltranslation.admin import TranslationAdmin

from articles import config
from articles.models import Article


def get_article_list_display():

    list_display = ['title']

    if config.IS_ARTICLE_TYPE_ENABLED:
        list_display += ['type']

    list_display += ['created']

    if config.ARE_COMMENTS_ENABLED:
        list_display += ['are_comments_enabled']

    return list_display + ['preview_tag']


def get_article_list_filter():

    list_filter = []

    if config.IS_ARTICLE_TYPE_ENABLED:
        list_filter += ['type']

    list_filter += ['created']

    if config.ARE_COMMENTS_ENABLED:
        list_filter += ['are_comments_enabled']

    return list_filter


@admin.register(Article)
class ArticleAdmin(TranslationAdmin):

    list_display = get_article_list_display()

    list_filter = get_article_list_filter()

    if config.ARE_TAGS_ENABLED:
        filter_horizontal = ['tags']

    def preview_tag(self, obj):
        return render_to_string('articles/admin/preview.html', {
            'file': obj.logo
        })

    preview_tag.short_description = _('Preview')


if config.IS_ARTICLE_TYPE_ENABLED:

    @admin.register(apps.get_model('articles', 'ArticleType'))
    class ArticleTypeAdmin(TranslationAdmin):

        list_display = ['name']
        search_fields = ['name']


if config.ARE_TAGS_ENABLED:

    @admin.register(apps.get_model('articles', 'ArticleTag'))
    class ArticleTagAdmin(TranslationAdmin):

        list_display = ['text']
        search_fields = ['text']
