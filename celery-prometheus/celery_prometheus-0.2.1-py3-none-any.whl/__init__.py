import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("celery_prometheus").version
except pkg_resources.DistributionNotFound:
    pass

from .prometheus_bootstep import add_prometheus_option
from .signals import prometheus_mark_celery_worker_dead  # noqa

__all__ = ["add_prometheus_option"]
