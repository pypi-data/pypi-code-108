import logging

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import ugettext as _

from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.views import (
    BaseRestView,
    Filter,
    FilterGroup,
    ModelFilter,
    RestView,
)
from pfx.pfxcore.views.rest_views import SlugDetailRestViewMixin

from .models import Author, Book, BookType

logger = logging.getLogger(__name__)


class AuthorRestViewMixin():
    queryset = Author.objects
    fields = ['first_name', 'last_name', 'name_length',
              'books', 'created_at', 'slug', 'gender']
    list_fields = ['first_name', 'last_name', 'gender']
    readonly_fields = ['created_at']


def heroic_fantasy_filter(value):
    q = Q(last_name="Tolkien")
    return value and q or ~q


def last_name_filter(value):
    return Q(last_name__isnull=not value)


def last_name_choices_filter(value):
    return Q(last_name=value)


def pub_date_gte_filter(value):
    return Q(pub_date__gte=value)


def author_pk_filter(value):
    return Q(author__pk=value)


@rest_view("/authors")
class AuthorRestView(AuthorRestViewMixin, SlugDetailRestViewMixin, RestView):
    default_public = True
    filters = [
        FilterGroup('book_gender', _("Book Gender"), [
            ModelFilter(Author, 'science_fiction'),
            Filter(
                'heroic_fantasy', _("Heroic Fantasy"),
                Filter.BooleanField, heroic_fantasy_filter),
        ]),
        FilterGroup('custom', _("Custom"), [
            ModelFilter(
                Author, 'last_name', type=Filter.BooleanField,
                filter_func=last_name_filter),
            ModelFilter(Author, 'first_name'),
            ModelFilter(Author, 'gender'),
            Filter(
                'last_name_choices', _("Tolien or Asimov"),
                Filter.CharField, last_name_choices_filter,
                choices=[('Tolkien', "Tolkien"), ('Asimov', "Asimov")]),
        ]),
    ]

    def search_filter(self, search):
        return (
            Q(first_name__unaccent__icontains=search) |
            Q(last_name__unaccent__icontains=search))


@rest_view("/private-edit/authors")
class PrivateEditAuthorRestView(AuthorRestViewMixin, RestView):
    get_public = True
    get_list_public = True


@rest_view("/private/authors")
class PrivateAuthorRestView(AuthorRestViewMixin, RestView):
    pass


@rest_view("/admin-edit/authors")
class AdminEditAuthorRestView(AuthorRestViewMixin, RestView):
    def put_perm(self, id, *args, **kwargs):
        return self.request.user.is_superuser


@rest_view("/admin/authors")
class AdminAuthorRestView(AuthorRestViewMixin, RestView):
    def perm(self):
        return self.request.user.is_superuser


@rest_view("/books")
class BookRestView(RestView):
    queryset = Book.objects
    fields = ['name', 'author', 'pub_date', 'created_at', 'type']
    readonly_fields = ['created_at']
    default_public = True
    filters = [
        FilterGroup('custom', _("Custom"), [
            ModelFilter(Book, 'author'),
            ModelFilter(Book, 'pages'),
            ModelFilter(Book, 'rating'),
            ModelFilter(Book, 'pub_date'),
            Filter(
                'pub_date_gte', _("Publication Date greater than"),
                Filter.DateField, pub_date_gte_filter),
            Filter(
                'author_pk', _("Author PK"),
                Filter.ForeignKey, author_pk_filter,
                related_model="Author"),
        ]),
    ]


@rest_view("/book-types")
class BookTypeRestView(RestView):
    queryset = BookType.objects
    fields = ['name', 'slug']
    readonly_fields = ['created_at']
    default_public = True


@rest_view("/test-i18n")
class Testi18nView(BaseRestView):
    default_public = True

    @rest_api("", method="get")
    def get(self, *args, **kwargs):
        return JsonResponse({'Monday': _("Monday")})


@rest_view("/error")
class TestErrorView(BaseRestView):
    default_public = True

    @rest_api("/500", method="get")
    def raise_500(self):
        raise ImproperlyConfigured("Test exception")
