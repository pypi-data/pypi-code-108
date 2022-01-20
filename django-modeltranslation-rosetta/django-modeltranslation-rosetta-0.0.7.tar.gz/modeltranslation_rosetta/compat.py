try:
    from django.urls import re_path as url, include  # noqa
except ImportError:
    from django.conf.urls import url, include  # noqa
