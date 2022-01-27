import pytest

from sym.sdk.integrations.slack import SlackError, channel, group, user


class TestSlackInterface:
    def test_errors(self):
        with pytest.raises(
            SlackError,
            match="An unexpected error occurred while trying to connect to Slack.",
        ) as slack_error:
            raise SlackError.UNKNOWN()

        assert slack_error.value.doc_url == "https://docs.symops.com/docs/support"

    def test_timeout_error(self):
        with pytest.raises(
            SlackError,
            match="Sym timed out while trying to connect to Slack.",
        ) as timeout_error:
            raise SlackError.TIMEOUT()

        assert timeout_error.value.doc_url == "https://docs.symops.com/docs/support"

    def test_signatures(self):
        assert user("user_id@simi.org") is None
        assert channel("channel_name") is None
        assert group(["a", "b"]) is None
