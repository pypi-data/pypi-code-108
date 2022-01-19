import pytz
from psu_base.models.downtime import Downtime
from psu_base.classes.Log import Log
from datetime import datetime, timedelta
from psu_base.services import utility_service, error_service

log = Log()


def get_next_downtime():
    """Get the next (includes current active) downtime"""
    try:
        now = datetime.now()
        cutoff = now + timedelta(minutes=20)

        if utility_service.get_setting('USE_TZ') and not now.tzinfo:
            america_vancouver = pytz.timezone('America/Vancouver')
            now = america_vancouver.localize(now)
            cutoff = america_vancouver.localize(cutoff)

        downtimes = (
            Downtime.objects.filter(from_date__lte=cutoff)
            .exclude(until_date__lte=now)
            .order_by("from_date")
        )
        if downtimes:
            return downtimes[0]
    except Exception as ee:
        error_service.record(ee)

    return None
