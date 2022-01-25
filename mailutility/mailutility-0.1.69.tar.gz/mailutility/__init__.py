from .mailmonitor import MailMonitor
from .mailsender import MailSender

try:
    from ._version import __version__
except ImportError:
    pass
