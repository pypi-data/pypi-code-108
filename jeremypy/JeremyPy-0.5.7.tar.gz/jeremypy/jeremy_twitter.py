from requests import get

from jeremypy.jeremy_config import JeremyConfig


class JeremyTwitter:
    def __init__(self, config):
        self.config = JeremyConfig(config)
        self.token = self.config.get('JeremyTwitter', 'TOKEN')

    def create_url_for_tid_lookup(self, tid):
        tweet_fields = 'tweet.fields=author_id,text'
        expansions = 'expansions=attachments.media_keys'
        media_fields = 'media.fields=type,url,preview_image_url'
        url = f'https://api.twitter.com/2/tweets?ids={tid}&{tweet_fields}&{expansions}&{media_fields}'
        return url

    def create_url_for_author_id_lookup(self, author_id):
        user_fields = 'user.fields=name,profile_image_url,username,verified'
        url = f'https://api.twitter.com/2/users?ids={author_id}&{user_fields}'
        return url

    def create_url_for_username_lookup(self, username):
        user_fields = 'user.fields=name,profile_image_url,username,verified'
        url = f'https://api.twitter.com/2/users/by?usernames={username}&{user_fields}'
        return url

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f'Bearer {self.token}'
        r.headers["User-Agent"] = 'JarvisMessengerBot'
        return r

    def connect_to_endpoint(self, url):
        response = get(url, auth=self.bearer_oauth)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def get_tweet_from_tid(self, tid):
        url = self.create_url_for_tid_lookup(tid)
        json_response = self.connect_to_endpoint(url)
        return json_response

    def get_user_from_author_id(self, author_id):
        url = self.create_url_for_author_id_lookup(author_id)
        json_response = self.connect_to_endpoint(url)
        return json_response

    def get_user_from_username(self, username):
        url = self.create_url_for_username_lookup(username)
        json_response = self.connect_to_endpoint(url)
        return json_response

    def get_original_profile_image_url_from_user(self, user):
        url = user['data'][0]['profile_image_url']
        return url.replace('_normal', '')

    def get_tweet_from_url(self, url):
        split_url = url.split('/')
        if 'status' in split_url:
            tid = split_url[split_url.index('status') + 1].split('?')[0]
            return self.get_tweet_from_tid(tid)
        elif 'twitter.com' in split_url and len(split_url) > split_url.index('twitter.com') + 1:
            username = split_url[split_url.index('twitter.com') + 1]
            return self.get_user_from_username(username)
        elif 'mobile.twitter.com' in split_url and len(split_url) > split_url.index('mobile.twitter.com') + 1:
            username = split_url[split_url.index('mobile.twitter.com') + 1]
            return self.get_user_from_username(username)

    def get_text_from_tweet(self, tweet):
        if 'text' not in tweet['data'][0]:
            return None
        text = tweet['data'][0]['text']
        stop_index = text.rfind('https://t.co/')
        if stop_index >= 0:
            if stop_index == 0:
                return ''
            text = text[0:stop_index-1]
        return text

    def get_media_url_from_tweet(self, tweet):
        if 'includes' in tweet and 'media' in tweet['includes']:
            if 'url' in tweet['includes']['media'][0]:
                return tweet['includes']['media'][0]['url']
            elif 'preview_image_url' in tweet['includes']['media'][0]:
                return tweet['includes']['media'][0]['preview_image_url']
        return None

    def get_author_id_from_tweet(self, tweet):
        if 'author_id' not in tweet['data'][0]:
            return None
        return tweet['data'][0]['author_id']

    def get_username_from_user(self, user):
        return user['data'][0]['username']

    def get_name_from_user(self, user):
        return user['data'][0]['name']

    def get_verified_from_user(self, user):
        return user['data'][0]['verified']

    def get_basic_tweet_info_from_url(self, url):
        tweet = self.get_tweet_from_url(url)
        text = self.get_text_from_tweet(tweet)
        media_url = self.get_media_url_from_tweet(tweet)
        author_id = self.get_author_id_from_tweet(tweet)
        if author_id:
            user = self.get_user_from_author_id(author_id)
            url_type = 'tweet'
        else:
            user = tweet
            url_type = 'user'
        username = self.get_username_from_user(user)
        name = self.get_name_from_user(user)
        profile_image_url = self.get_original_profile_image_url_from_user(user)
        verified = self.get_verified_from_user(user)
        return {
            'type': url_type,
            'name': name,
            'username': username,
            'profile_image_url': profile_image_url,
            'text': text,
            'media_url': media_url,
            'verified': verified
        }
