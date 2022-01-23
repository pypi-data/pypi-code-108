
from articles import defaults


class DefaultArticleSettings(object):

    IS_ARTICLE_TYPE_ENABLED = defaults.IS_ARTICLE_TYPE_ENABLED
    IS_ARTICLE_HITCOUNT_ENABLED = defaults.IS_ARTICLE_HITCOUNT_ENABLED
    ARE_COMMENTS_ENABLED = defaults.ARE_COMMENTS_ENABLED

    @property
    def INSTALLED_APPS(self):
        apps = super().INSTALLED_APPS

        if self.IS_ARTICLE_HITCOUNT_ENABLED and 'hitcount' not in apps:
            apps += ['hitcount']

        if self.ARE_COMMENTS_ENABLED and 'comments' not in apps:
            apps += ['comments']

        return apps + ['articles']

default = DefaultArticleSettings
