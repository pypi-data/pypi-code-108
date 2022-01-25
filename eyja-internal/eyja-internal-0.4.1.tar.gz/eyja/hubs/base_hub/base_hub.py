class BaseHub:
    _initialized = False

    @classmethod
    async def init(cls):
        cls._initialized = True

    @classmethod
    def sync_init(cls):
        cls._initialized = True

    @classmethod
    async def reset(cls):
        cls._initialized = False

    @classmethod
    def is_initialized(cls):
        return cls._initialized
