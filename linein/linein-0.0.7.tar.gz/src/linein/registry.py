__all__ = ['RegistryManager', 'manager', 'register', 'load_data', 'load_all_data']

from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import RelatedField
from .loader import NullLoader


class Singleton(object):
    """A do-nothing class.
    From A. Martelli et al. Python Cookbook. (O'Reilly)
    Thanks to Juergen Hermann."""
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst


class RegistryManager(Singleton):
    DEFAULT_CATEGORY = 'default'
    _pool = {}

    def register(self, loader_class, category=DEFAULT_CATEGORY, source=None):
        key = (self._get_model_path(loader_class.model), category)
        self._pool[key] = loader_class(source=source)

    def _get_model_path(self, model):
        content_type = ContentType.objects.get_for_model(model)
        return '{}.{}'.format(content_type.app_label, content_type.model)

    def get_loader(self, model, category=DEFAULT_CATEGORY):
        key = (self._get_model_path(model), category)
        loader = self._pool.get(key, None)
        if loader is None:
            return NullLoader()
        else:
            return loader

    def clear(self):
        self._pool.clear()

    def load_all_data(self, category=DEFAULT_CATEGORY):
        memo = set()
        for (model_path, cat), loader in self._pool.items():
            if cat == category:
                self._load_data(loader.model, category=category, with_deps=True, memo=memo)

    def load_data(self, model, category=DEFAULT_CATEGORY, with_deps=False):
        self._load_data(model, category=category, with_deps=with_deps, memo=None)

    def _load_data(self, model, category=DEFAULT_CATEGORY, with_deps=False, memo=None):
        def _use_memo():
            nonlocal memo
            return isinstance(memo, set)

        if _use_memo() and model in memo:
            return
        loader = self.get_loader(model, category=category)

        if with_deps and loader.model is not None:
            for field in loader.model._meta.get_fields(include_hidden=True):
                if isinstance(field, RelatedField):
                    dep_model = field.related_model
                    self._load_data(dep_model, category=category, with_deps=True, memo=memo)

        print("Loading {} data for {}".format(category, model))
        loader.load()
        if _use_memo():
            memo.add(model)


manager = RegistryManager()

register = manager.register
load_data = manager.load_data
load_all_data = manager.load_all_data
