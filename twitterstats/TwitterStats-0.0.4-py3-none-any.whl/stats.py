import json
from twitterstatsazure.api_client import get_followers, get_tweets
from twitterstatsazure.secrets import AZURE_CONNECTION_STRING


def store_json_to_azure(data, fname, container_name="containertest1"):
    import os, uuid
    from azure.storage.blob import (
        BlobServiceClient,
        BlobClient,
        ContainerClient,
        __version__,
    )

    try:
        print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")
        # Quick start code goes here

    except Exception as ex:
        print("Exception:")
        print(ex)

        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_CONNECTION_STRING
        )
    # Create a unique name for the container
    # container_name = str("containertest1")

    # Create the container
    # container_client = blob_service_client.create_container(container_name)

    # container_client = blob_service_client.get_container_client(container_name)

    blob_service_client: BlobServiceClient
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob="test4"
    )
    blob_client.upload_blob(json.dumps(data))


def update_user(db_user, user, now):
    # user = list(user)
    # assert len(user) == 1
    # user = user[0]

    for _ in list(user):
        if str(_["id"]) == str(db_user.twitter_id):
            break
    if str(_["id"]) == str(db_user.twitter_id):
        user = _
    else:
        raise Exception("No data retrieved.")

    db_user.twitter_username = user.get("username")
    db_user.twitter_name = user.get("name")
    db_user.twitter_verified = user.get("verified")
    db_user.twitter_description = user.get("description")
    db_user.twitter_join_date = user.get("created_at")
    db_user.twitter_profile_pic = user.get("profile_image_url")
    db_user.twitter_followers_count = user.get("public_metrics", {}).get(
        "followers_count"
    )
    db_user.twitter_following_count = user.get("public_metrics", {}).get(
        "following_count"
    )
    db_user.twitter_tweet_count = user.get("public_metrics", {}).get("tweet_count")
    db_user.twitter_listed_count = user.get("public_metrics", {}).get("listed_count")
    db_user.save()
    metrics = TwitterUserPublicMetrics(
        twitter_user=db_user,
        as_of=now,
        followers_count=user.get("public_metrics", {}).get("followers_count"),
        following_count=user.get("public_metrics", {}).get("following_count"),
        tweet_count=user.get("public_metrics", {}).get("tweet_count"),
        listed_count=user.get("public_metrics", {}).get("listed_count"),
    )
    metrics.save()


def update_tweets(twitter_user, tweets, now, update=True, promoted=False):
    for i, tweet in enumerate(tweets):
        # print("TW", i)
        # if str(tweet['id']) == '1452607419440267267':
        #     print(tweet)
        # if 'organic_metrics' in tweet.keys():
        #     print(tweet['organic_metrics'])
        base_query = Tweet.objects.filter(twitter_id=tweet["id"])
        if base_query.count():
            db_tweet = base_query.get()
            if update:
                db_tweet.text = tweet.get("text")
                db_tweet.twitter_created_at = tweet.get("created_at")
                db_tweet.is_promoted = promoted
                db_tweet.is_reply = bool(tweet.get("in_reply_to_user_id", False))
                db_tweet.save()
        else:
            db_tweet = Tweet(
                twitter_id=tweet["id"],
                author=twitter_user,
                text=tweet.get("text"),
                twitter_created_at=tweet.get("created_at"),
                is_promoted=promoted,
                is_reply=bool(tweet.get("in_reply_to_user_id", False)),
            )
            db_tweet.save()
        db_tweet = Tweet.objects.get(
            pk=db_tweet.pk
        )  # TODO: This is only needed to gather the `datetime` obj from `twitter_created_at`
        o = TweetMetrics(
            as_of=now, tweet=db_tweet, tweet_lifetime=now - db_tweet.twitter_created_at
        )

        public_metrics = tweet.get("public_metrics", None)
        if public_metrics:
            update_public_metrics(o, public_metrics)
        non_public_metrics = tweet.get("non_public_metrics", None)
        if non_public_metrics:
            update_non_public_metrics(o, non_public_metrics)
        organic_metrics = tweet.get("organic_metrics", None)
        if organic_metrics:
            update_organic_metrics(o, organic_metrics)
        promoted_metrics = tweet.get("promoted_metrics", None)
        if promoted_metrics:
            update_promoted_metrics(o, promoted_metrics)


def t1():
    import datetime
    from .api_client import get_user

    now = datetime.datetime.now()  # TODO: Time Zone
    twitter_user_id = "1183745466250477569"  # pythonicnews

    a = list(get_user([twitter_user_id]))
    print(a)


def t2():
    import datetime
    from .api_client import get_user

    now = datetime.datetime.now()  # TODO: Time Zone
    twitter_user_id = "1183745466250477569"  # pythonicnews

    a = list(get_tweets(twitter_user_id, promoted=False))
    print(a)


def get_follower_data():
    import datetime
    from .api_client import get_followers

    now = datetime.datetime.now()  # TODO: Time Zone
    twitter_user_id = "1183745466250477569" # pythonicnews

    a = list(get_followers(twitter_user_id))
    # return a


    fname = f"FOLLOWER_{now.isoformat()}.json"
    store_json_to_azure(a, fname)

    return a

