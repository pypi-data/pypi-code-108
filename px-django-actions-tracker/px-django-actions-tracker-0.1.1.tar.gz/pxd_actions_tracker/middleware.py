from .cases import uuid_track


__all__ = 'tracking_middleware',


def tracking_middleware(get_response):
    def runner(request):
        with uuid_track():
            response = get_response(request)
        return response

    return runner
