# from flask-redis
# https://github.com/underyx/flask-redis

try:
    import redis
except ImportError:
    # We can allow custom provider only usage without redis-py being installed
    redis = None

__all__ = ('FlaskRedis', )
__version__ = '0.5.0'


class FlaskRedis(object):

    def __init__(self, app=None, strict=True, config_prefix="REDIS", **kwargs):
        self.provider_class = redis.StrictRedis if strict else redis.Redis
        self.provider_kwargs = kwargs
        self.config_prefix = config_prefix

        self.config_uri = '{}_URI'.format(config_prefix)
        self.config_binds = '{}_BINDS'.format(config_prefix)
        # 保存 REDIS_URI 中设定的那个连接
        self._redis_client = None
        # 以 bind_key 保存 Client，其中 self._redis_client 将 None 作为 bind_key 保存
        self._redis_binds = None

        if app is not None:
            self.init_app(app)

    @classmethod
    def from_custom_provider(cls, provider, app=None, **kwargs):
        assert provider is not None, 'your custom provider is None, come on'

        # We never pass the app parameter here, so we can call init_app
        # ourselves later, after the provider class has been set
        instance = cls(**kwargs)

        instance.provider_class = provider
        if app is not None:
            instance.init_app(app)
        return instance

    def init_app(self, app, **kwargs):
        redis_url = app.config.get(
            self.config_uri, 'redis://localhost:6379/0'
        )

        self.provider_kwargs.update(kwargs)
        self._redis_client = self.provider_class.from_url(
            redis_url, **self.provider_kwargs
        )

        self._update_binds(app)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions[self.config_prefix.lower()] = self

    def _update_binds(self, app):
        redis_binds = app.config.get(self.config_binds)
        self._redis_binds = {
            None: self._redis_client
        }
        if isinstance(redis_binds, dict):
            for bind_key, bind_uri in redis_binds.items():
                self._redis_binds[bind_key] = self.provider_class.from_url(
                    bind_uri, **self.provider_kwargs
                )

    def get_client(self, bind_key=None):
        return self._redis_binds.get(bind_key)

    def get_clients(self):
        return self._redis_binds

    def __getattr__(self, name):
        return getattr(self._redis_client, name)

    def __getitem__(self, name):
        return self._redis_client[name]

    def __setitem__(self, name, value):
        self._redis_client[name] = value

    def __delitem__(self, name):
        del self._redis_client[name]