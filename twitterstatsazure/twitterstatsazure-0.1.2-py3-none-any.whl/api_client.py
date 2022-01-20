import time
from TwitterAPI import (
    TwitterAPI,
    TwitterRequestError,
    TwitterConnectionError,
    HydrateType,
)
from .secrets import *


MAX_MAX_RESULTS_USER = 1000  # https://developer.twitter.com/en/docs/twitter-api/users/follows/quick-start/follows-lookup
MAX_MAX_RESULTS_TWEET = 100


api = TwitterAPI(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    api_version="2",
)


def api_request(endpoint, *args, try_count=0, **kwargs):
    """Wrapper for api.request"""
    # TODO: The TwitterRequestError is not catched!!! This is because the exception is raised in __iter__
    print("API_REQUEST")
    try:
        res = api.request(endpoint, *args, **kwargs)
        res.get_iterator()
        return res
    except TwitterRequestError as e:
        print(">Request error")
        print(e.status_code)
        for msg in iter(e):
            print(msg)
        print("RES IS NOW", res)
        if try_count < 2:
            print("Retry in 15 min")
            time.sleep(15 * 60)
            return api_request(endpoint, try_count=try_count + 1, *args, **kwargs)
        else:
            print("Max retries reached", try_count)
        res = None
    except TwitterConnectionError as e:
        res = None
        print("Connection error")
        print(e)
    except Exception as e:
        res = None
        print("Exception")
        print(e)
    return res


def get_tweets(USER_ID, promoted=False):
    tweets = api.request(f"users/:{USER_ID}/tweets")
    params = {
        "max_results": MAX_MAX_RESULTS_TWEET,
        "tweet.fields": "created_at,public_metrics,non_public_metrics,in_reply_to_user_id",
    }
    if promoted:
        params["tweet.fields"] += ",organic_metrics,promoted_metrics"
    r = api_request(f"users/:{USER_ID}/tweets", params)
    return r
    return [item for item in r]


def get_tweet(TWEET_ID, promoted=True):
    print("Get tweet", TWEET_ID, promoted)

    # EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
    EXPANSIONS = "author_id"
    # MEDIA_FIELDS = 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics'
    MEDIA_FIELDS = "public_metrics"
    # TWEET_FIELDS = 'created_at,author_id,public_metrics,context_annotations,entities'
    TWEET_FIELDS = (
        "public_metrics,non_public_metrics,promoted_metrics,entities,organic_metrics"
    )
    # USER_FIELDS = 'location,profile_image_url,verified'
    USER_FIELDS = "verified"

    if not promoted:
        TWEET_FIELDS = "public_metrics,non_public_metrics,entities"

    endpoint = f"tweets/:{TWEET_ID}"
    params = {
        "expansions": EXPANSIONS,
        "tweet.fields": TWEET_FIELDS,
        "user.fields": USER_FIELDS,
        "media.fields": MEDIA_FIELDS,
    }
    if isinstance(TWEET_ID, list):
        TWEET_ID = ",".join(TWEET_ID)
        params["ids"] = TWEET_ID
        endpoint = f"tweets"

    try:
        # o = TwitterOAuth.read_file()
        # api = TwitterAPI(o.consumer_key, o.consumer_secret, o.access_token_key, o.access_token_secret, api_version='2')
        r = api.request(endpoint, params, hydrate_type=HydrateType.APPEND)
        r = [item for item in r]
        if promoted and not r:
            return get_tweet(TWEET_ID, promoted=False)
        return r

    except TwitterRequestError as e:
        print("TwitterRequestError")
        print(e.status_code)
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print("TwitterConnectionError")
        print(e)

    except Exception as e:
        print("Exception")
        print(e)


def get_followers(USER_ID):
    params = {
        "max_results": MAX_MAX_RESULTS_USER,
        "user.fields": "id,name,username,created_at,description,profile_image_url,public_metrics,url,verified",
    }

    followers = api_request(f"users/:{USER_ID}/followers", params)
    if followers:
        for i, f in enumerate(followers):
            yield f
        try:
            next_token = followers.json()["meta"]["next_token"]
        except KeyError:
            next_token = None
        print("NEXT_TOKEN", next_token)
        while next_token:
            params["pagination_token"] = next_token
            followers = api_request(f"users/:{USER_ID}/followers", params)
            if followers:
                for i, f in enumerate(followers):
                    yield f
                try:
                    next_token = followers.json()["meta"]["next_token"]
                except KeyError:
                    next_token = None


def get_user(USER_ID):
    params = {
        "user.fields": "id,name,username,created_at,description,profile_image_url,public_metrics,url,verified"
    }
    if isinstance(USER_ID, list):
        params["ids"] = ",".join(USER_ID)
        users = api_request(f"users", params)
    else:
        users = api_request(f"users/:{USER_ID}", params)
    for user in users:
        yield user
