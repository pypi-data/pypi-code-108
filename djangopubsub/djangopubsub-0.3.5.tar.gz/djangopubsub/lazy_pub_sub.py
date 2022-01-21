from django.utils.functional import LazyObject

from djangopubsub import DjangoPubSub


class LazyPubSub(LazyObject):

    def _setup(self):
        self._wrapped = DjangoPubSub()
