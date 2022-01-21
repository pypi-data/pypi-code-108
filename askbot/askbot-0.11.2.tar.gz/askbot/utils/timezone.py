from django.utils import timezone
from django.conf import settings as django_settings
from pytz.exceptions import AmbiguousTimeError, NonExistentTimeError

def make_aware(value, tz=None):
    """
    Makes a naive datetime.datetime in a given time zone aware.

    If conversion is ambigous regarding the daytime savings,
    assume that the daytime savings is on, b/c we
    don't care about such exactitude here
    """
    if tz is None:
        tz_code = django_settings.TIME_ZONE
        tz = timezone.pytz.timezone(tz_code)

    if hasattr(tz, 'localize'):
        # This method is available for pytz time zones.
        dst = tz.localize(value, True)
        no_dst = tz.localize(value, False)
        if dst == no_dst:
            return dst
        try:
            return tz.localize(value, is_dst=None)
        except (AmbiguousTimeError, NonExistentTimeError):
            return tz.localize(value, is_dst=False)
        except NonExistentTimeError:
            return tz.localize(value, is_dst=True)


    # Check that we won't overwrite the timezone of an aware datetime.
    if timezone.is_aware(value):
        raise ValueError(
            "make_aware expects a naive datetime, got %s" % value)
    # This may be wrong around DST changes!
    return value.replace(tzinfo=tz)
