from django.shortcuts import render
from django.utils.encoding import force_text


def throttling_failure_view(request, exception):
    response = render(request, '429.html', {'description': force_text(exception)})
    response.status_code = 429
    return response
