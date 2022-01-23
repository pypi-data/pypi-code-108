
from random import randint

from django.apps import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property

from articles import config

from ckeditor_uploader.fields import RichTextUploadingField
from slugify import slugify_url


if config.IS_ARTICLE_TYPE_ENABLED:

    class ArticleType(models.Model):

        name = models.CharField(_('Name'), max_length=255, unique=True)

        slug = models.CharField(
            _('Slug'), max_length=255, db_index=True, unique=True)

        def __str__(self):
            return self.name

        class Meta:
            verbose_name = _('Article type')
            verbose_name_plural = _('Article types')


if config.ARE_TAGS_ENABLED:

    class ArticleTag(models.Model):

        text = models.CharField(_('Text'), max_length=255, unique=True)

        def __str__(self):
            return self.text

        class Meta:
            verbose_name = _('Article tag')
            verbose_name_plural = _('Article tags')


class Article(models.Model):

    if config.IS_ARTICLE_TYPE_ENABLED:
        type = models.ForeignKey(
            ArticleType, verbose_name=_('Type'), blank=True, null=True,
            related_name='articles', on_delete=models.SET_NULL)

    title = models.CharField(_('Title'), max_length=255)

    logo = models.ImageField(
        blank=True, null=True, upload_to='article_logos')

    description = models.CharField(_('Description'), max_length=255)

    text = RichTextUploadingField(_('Text'), max_length=50000)

    created = models.DateTimeField(_('Created'), db_index=True)

    author = models.CharField(_('Author'), max_length=255, blank=True)

    if config.ARE_COMMENTS_ENABLED:
        are_comments_enabled = models.BooleanField(
            _('Are comments enabled'), default=True)

    if config.ARE_TAGS_ENABLED:
        tags = models.ManyToManyField(
            ArticleTag,
            verbose_name=_("Tags"),
            related_name='tags',
            blank=True)

    @classmethod
    def most_popular(cls, article_type=None):

        if not config.IS_ARTICLE_HITCOUNT_ENABLED:
            raise Exception('Hitcount is disabled')

        ct = ContentType.objects.get_for_model(cls)

        hitcount = apps.get_model('hitcount', 'HitCount')

        ids = hitcount.objects.filter(content_type=ct).order_by('-hits')\
            .values_list('object_pk', flat=True)

        queryset = cls.objects.filter(
            id__in=ids
        )

        if article_type:
            queryset = queryset.filter(type__slug=article_type)

        return queryset.extra(
            select={
                'manual': 'FIELD(articles_article.id,{})'.format(
                    ','.join(map(str, ids)))
            },
            order_by=['manual']
        )

    @classmethod
    def get_related_articles(cls, article_type=None, exclude_pk=None, count=6):

        index = 0

        queryset = cls.objects.all()

        if article_type:
            queryset = queryset.filter(type__slug=article_type)

        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)

        related_articles_count = queryset.count()

        if related_articles_count:

            if related_articles_count > count:
                index = randint(0, related_articles_count - count)

            return queryset[index:index + count]

        return []

    @cached_property
    def related_articles(self):
        return self.get_related_articles(
            article_type=self.type.slug if self.type else None,
            exclude_pk=self.pk)

    @property
    def hits(self):
        hitcount = apps.get_model('hitcount', 'HitCount')
        return hitcount.objects.get_for_object(self).hits

    @property
    def slug(self):
        return slugify_url(self.title, separator='_')

    def __str__(self):
        return self.title

    def get_absolute_url(self):

        params = {'slug': self.slug, 'id': self.pk}

        if config.IS_ARTICLE_TYPE_ENABLED:
            params['type'] = self.type.slug

        return reverse_lazy('articles:info', kwargs=params)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-created']
