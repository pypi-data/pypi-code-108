from django.middleware.common import CommonMiddleware as DjangoCommonMiddleware


class CommonMiddleware(DjangoCommonMiddleware):
    def process_response(self, request, response):
        super().process_response(request, response)

        if (request.method == 'HEAD' and
                (response.content is None or response.content == b'')):
            del response['Content-Length']

        return response
