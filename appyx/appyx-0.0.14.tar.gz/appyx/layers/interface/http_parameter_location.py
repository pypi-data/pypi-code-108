class HttpParameterLocation:
    def get_argument_from_request(self, parameter, request, kwargs, default=None):
        raise NotImplementedError('Subclass responsibility')

    @classmethod
    def path(cls):
        return PathHttpParameter()

    @classmethod
    def data(cls):
        return DataHttpParameter()

    @classmethod
    def query(cls):
        return QueryHttpParameter()

    @classmethod
    def file(cls):
        return FileHttpParameter()

    @classmethod
    def auth(cls):
        return AuthHttpParameter()


# TODO: add support to path parameters and implement this. This needs that the handler is decoupled from the APIView
class PathHttpParameter(HttpParameterLocation):
    def get_argument_from_request(self, parameter, request, kwargs, default=None):
        return kwargs.get(parameter.name(), default)


class DataHttpParameter(HttpParameterLocation):
    def get_argument_from_request(self, parameter, request, kwargs, default=None):
        return request.data.get(parameter.name(), default)


class QueryHttpParameter(HttpParameterLocation):
    def get_argument_from_request(self, parameter, request, kwargs, default=None):
        return request.GET.get(parameter.name(), default)


class FileHttpParameter(HttpParameterLocation):
    def get_argument_from_request(self, parameter, request, kwargs, default=None):
        return request.FILES.get(parameter.name(), default)


class AuthHttpParameter(HttpParameterLocation):
    def get_argument_from_request(self, parameter, request, kwargs, default=None):
        return request.auth
