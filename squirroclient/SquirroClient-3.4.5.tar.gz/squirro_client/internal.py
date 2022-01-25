import logging

from .base import SquirroClient
from .topic import TopicApiMixin
from .user import UserApiMixin

log = logging.getLogger(__name__)


class PlatformSquirroClient(SquirroClient, UserApiMixin, TopicApiMixin):
    """Squirro client to be used by the Squirro platform components."""

    def __init__(self, *args, **kwargs):
        """Constructor for a new platform Squirro client."""
        super(PlatformSquirroClient, self).__init__(*args, **kwargs)

        # extract the supported callbacks
        # - on_refresh_token
        # - before_token_refresh, expected to return a dictionary to be passed
        #   on to `_refresh_tokens` as keyword arguments
        self._callback_on_token_refresh = kwargs.get("on_token_refresh", None)
        if self._callback_on_token_refresh is not None:
            assert callable(self._callback_on_token_refresh)

        self._before_token_refresh = kwargs.get("before_token_refresh", None)
        if self._before_token_refresh is not None:
            assert callable(self._before_token_refresh)

        # extract the supported helper methods
        self._helper_get_refresh_token = kwargs.get("get_refresh_token", None)
        if self._helper_get_refresh_token is not None:
            assert callable(self._helper_get_refresh_token)

    def _on_token_refresh(self, access_token, refresh_token):
        """Method to be called if a new access token has been received for the
        user. The corresponding callback function is invoked as well. Notice
        that if the callback function raises an exception it needs to be
        handled or the regular execution flow will not continue.
        """

        # call parent function
        super(PlatformSquirroClient, self)._on_token_refresh(
            access_token, refresh_token
        )

        # safely invoke callback
        try:
            if self._callback_on_token_refresh:
                self._callback_on_token_refresh(access_token, refresh_token)
        except Exception as ex:
            log.debug("error during callback invocation: %r", ex)
            raise

    def _refresh_tokens(self):
        """Refresh the access token by using the refresh token. If provided
        the access token is gathered using the external helper function.
        """

        kwargs = {}
        if self._before_token_refresh:
            kwargs = self._before_token_refresh()

        # call parent function
        ret = super(PlatformSquirroClient, self)._refresh_tokens(**kwargs)
        if ret:
            return ret

        # if that request was not successful, get refresh token via external
        # helper function
        try:
            if self._helper_get_refresh_token:
                token = self._helper_get_refresh_token()
                log.debug("helper invocation yielded refresh token %r", token)
                self.refresh_token = token
        except Exception as ex:
            log.debug("error during helper invocation: %r", ex)
            raise

        # call parent function again
        ret = super(PlatformSquirroClient, self)._refresh_tokens(**kwargs)
        return ret
