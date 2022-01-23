
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView


from pagination import PaginationMixin

from articles import config
from articles.models import Article


class ArticleListView(PaginationMixin, ListView):

    template_name = 'articles/list.html'
    paginate_by = 10
    queryset = Article.objects.all()

    if config.IS_ARTICLE_TYPE_ENABLED:

        def get(self, request, *args, **kwargs):
            self.article_type = get_object_or_404(
                apps.get_model('articles', 'ArticleType'),
                slug=kwargs['type'])
            return super(ArticleListView, self).get(request, *args, **kwargs)

        def get_queryset(self):
            return self.article_type.articles.all()

        def get_context_data(self, **kwargs):
            cxt = super(ArticleListView, self).get_context_data(**kwargs)
            cxt['article_type'] = self.article_type
            return cxt


def get_detail_view_class():

    if config.IS_ARTICLE_HITCOUNT_ENABLED:
        from hitcount.views import HitCountDetailView
        return HitCountDetailView

    return DetailView


class ArticleDetailView(get_detail_view_class()):

    template_name = 'articles/detail.html'
    count_hit = True

    def get_object(self, queryset=None):

        params = {'pk': self.kwargs['id']}

        if config.IS_ARTICLE_TYPE_ENABLED:
            params['type__slug'] = self.kwargs['type']

        return get_object_or_404(Article, **params)
