from django.conf import settings
from expressmoney.utils import get_ip


def allowed_ip(request):
    user_ip = get_ip(request)

    for allow_ip in settings.ALLOWED_IP:
        if user_ip == allow_ip or user_ip.startswith(allow_ip):
            return True
    return False


def fix_flow_signal(func):
    def _wrapper_fix_signal(self, **kwargs):
        kwargs.update({'self': self})
        func(**kwargs)

    return _wrapper_fix_signal
