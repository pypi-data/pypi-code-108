
__API_REGISTRY = dict()


def api(api_identity: str):
    api_module = __API_REGISTRY[api_identity] if api_identity in __API_REGISTRY else None
    if api_module:
        return api_module
    api_module = Api(api_identity)
    __API_REGISTRY[api_identity] = api_module
    return api_module


class Api:

    def __init__(self, id: str):
        super().__init__()
        self.url = 'http://localhost:8081'
        self.id = id
