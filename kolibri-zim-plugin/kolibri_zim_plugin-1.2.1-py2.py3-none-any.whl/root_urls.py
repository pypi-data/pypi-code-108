from django.conf.urls import url

from .views import ZimArticleView
from .views import ZimIndexView
from .views import ZimRandomArticleView
from .views import ZimSearchView

urlpatterns = [
    url(
        r"^zim/content/(?P<zim_filename>[^/]+.zim)$",
        ZimIndexView.as_view(),
        name="zim_index",
    ),
    url(
        r"^zim/content/(?P<zim_filename>[^/]+.zim)/(?P<zim_article_path>.+)$",
        ZimArticleView.as_view(),
        name="zim_article",
    ),
    url(
        r"^zim/random/(?P<zim_filename>[^/]+.zim)$",
        ZimRandomArticleView.as_view(),
        name="zim_random_article",
    ),
    url(
        r"^zim/search/(?P<zim_filename>[^/]+.zim)$",
        ZimSearchView.as_view(),
        name="zim_search",
    ),
]
