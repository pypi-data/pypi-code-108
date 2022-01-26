from ..config import SLACK_URL
from ..logger import GLOBAL_LOGGER as log
from .alerting.slack import SlackAlert
from .alerting.dummy import DummyAlert


# Alerting factory
def init():
    if SLACK_URL:
        log.info("Using slack alerting.")
        return SlackAlert(SLACK_URL)
    else:
        log.info("Alerting is not enabled.")
        return DummyAlert()
