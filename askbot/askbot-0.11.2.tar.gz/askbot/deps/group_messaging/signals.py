import django.dispatch

thread_created = django.dispatch.Signal(providing_args=['message',])
response_created = django.dispatch.Signal(providing_args=['message',])
