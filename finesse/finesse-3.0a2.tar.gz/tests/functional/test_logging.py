import logging
import pytest
from finesse.utilities import logs


# NOTE: pytest caplog seems to ignore the configured log format, so setting `fmt` and
# `datefmt` below has no effect.
@pytest.mark.parametrize(
    "context_level", ("debug", "info", "warning", "error", "critical")
)
@pytest.mark.parametrize(
    "message_level", ("debug", "info", "warning", "error", "critical")
)
@pytest.mark.parametrize("channel", ("finesse", "finesse.mod1", "finesse.mod1.mod2"))
def test_log_context(caplog, context_level, message_level, channel):
    """Test log context manager.

    Notes
    -----
    Pytest's caplog fixture uses its own handler and so the channel exclude and
    formatting features of :func:`.logs` can't be tested.
    """
    message_level = logging.getLevelName(message_level.upper())
    context_level = logging.getLevelName(context_level.upper())

    with logs(logging.getLogger(), level=context_level):
        logger = logging.getLogger(channel)
        logger.log(message_level, "__test__")

        if message_level >= context_level:
            assert len(caplog.records) == 1
            assert caplog.records[0].getMessage() == "__test__"
        else:
            assert len(caplog.records) == 0
