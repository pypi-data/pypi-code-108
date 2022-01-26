from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.admin.options import TabularInline
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse


class ArticleFormSetMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['text'].required = False
            form.fields['title'].required = False


class ArticleInlineMixin:
    extra = 0
    fieldsets = (
        (_('Optional'), {
            'fields': ('sortorder', 'title', 'text'),
            'classes': ('collapse', 'mb-5')
        }),
        (None, {
            'fields': ('image', 'url')
        }),
    )
