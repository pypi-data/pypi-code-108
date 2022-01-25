class BasePlugin:
    name = None
    plugin_type = None

    @classmethod
    async def run(cls, **params):
        pass
