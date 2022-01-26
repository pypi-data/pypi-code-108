from sys import api_version
import time
from TwitterAPI import (
    TwitterAPI,
    TwitterPager,
    TwitterRequestError,
    TwitterConnectionError,
)


class TwitterStats:
    MAX_MAX_RESULTS_USER = 1000  # https://developer.twitter.com/en/docs/twitter-api/users/follows/quick-start/follows-lookup
    MAX_MAX_RESULTS_TWEET = 100

    def __init__(
        self,
        *,
        consumer_key=None,
        consumer_secret=None,
        access_token=None,
        access_token_secret=None,
        twitter_api_object=None,
    ):
        if twitter_api_object is not None:
            if not isinstance(twitter_api_object, TwitterAPI):
                raise ValueError(
                    "Parameter `twitter_api_object` must be a `TwitterAPI` object."
                )
            x = [
                param is None
                for param in [
                    consumer_key,
                    consumer_secret,
                    access_token,
                    access_token_secret,
                ]
            ]
            if not all(x):
                raise ValueError(
                    "Parameter `twitter_api_object` provided along with Auth Secrets"
                )
            self._twitter_api_object = twitter_api_object
        elif all(
            [
                param is not None
                for param in [
                    consumer_key,
                    consumer_secret,
                    access_token,
                    access_token_secret,
                ]
            ]
        ):
            self._twitter_api_object = TwitterAPI(
                consumer_key, consumer_secret, access_token, access_token_secret, api_version="2"
            )
        else:
            raise ValueError(
                "Either (`consumer_key`, `consumer_secret`, `access_token`, `access_token_secret`) or `twitter_api_object` has to be provided."
            )
        self._user_id = self._set_user_id(force=True)

    def _set_user_id(self, force=False):
        if not self._user_id or force:
            my_user = self._twitter_api_object.request(f"users/:me")
            self._user_id = my_user.json()["data"]["id"]
        return self._user_id

    def get_tweets(self, promoted=False):
        USER_ID = self._user_id
        params = {
            "max_results": self.MAX_MAX_RESULTS_TWEET,
            "tweet.fields": "created_at,public_metrics,non_public_metrics,in_reply_to_user_id",
        }
        if promoted:
            params["tweet.fields"] += ",organic_metrics,promoted_metrics"
        pager = TwitterPager(
            self._twitter_api_object, f"users/:{USER_ID}/tweets", params
        )
        return list(pager.get_iterator())

    def get_followers(self):
        USER_ID = self._user_id
        params = {
            "max_results": self.MAX_MAX_RESULTS_USER,
            "user.fields": "id,name,username,created_at,description,profile_image_url,public_metrics,url,verified",
        }
        pager = TwitterPager(
            self._twitter_api_object, f"users/:{USER_ID}/followers", params
        )
        return list(pager.get_iterator())
