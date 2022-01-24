import sys
from googleapiclient.discovery import build
import json
from googleapiclient.errors import HttpError
from configparser import ConfigParser
import os
from httplib2 import ServerNotFoundError
from youtube_transcript_api import YouTubeTranscriptApi
import re

CONFIG = "config.ini"
config = ConfigParser(allow_no_value=True)
config.read(CONFIG)
TIME_DELTA = int(config.get("main", "default_time_crawler"))
DEFAULT_RAW_FINAL_FILE = "FINAL_raw_merged.json"  # within {RAW_PARENT_PATH}
DEFAULT_CHANNEL_FINAL_FILE = "FINAL_channel_merged.json"  # within {CHANNEL_PARENT_PATH}


# TODO: Work on setup_channel for different extensions

class _CrawlerObject():
    def __init__(self):

        # more permanent
        self.DEVELOPER_KEY = None
        self.YOUTUBE_API_SERVICE_NAME = None
        self.YOUTUBE_API_VERSION = None
        self.KEYS_PATH = None
        self.TIME_DELTA = None
        self.DEFAULT_RAW_FINAL_FILE = None
        self.DEFAULT_CHANNEL_FINAL_FILE = None
        self.codes = []
        self.search_key = "YouTube"
        self.CURRENT_ROOT = self.search_key + "/"

        # more changing
        self.youtube = None
        self.code_index = -1

        # depends more on user's config
        self.RAW_PARENT_PATH = None

    def build(self, destination):
        self._fetch_vars()

        destination_list = [self.video_search_files, self.channel_search_files, self.video_data_files,
                            self.subtitle_subtitle_dir]

        self.search_key = destination  # by default, the search key is the dataset name
        self.CURRENT_ROOT = self.search_key + "/"
        try:
            os.mkdir(self.search_key)
        except OSError:
            print("Directory already exists %s" % self.search_key)
        else:
            print("Successfully created the directory %s " % self.search_key)

        for dest in destination_list:
            try:
                os.mkdir(self.search_key + "/" + dest)
            except OSError:
                print("Directory already exists %s" % dest)
            else:
                print("Successfully created the directory %s " % dest)

        # api
        try:
            self._try_next_id()
            self.youtube = build(
                self.YOUTUBE_API_SERVICE_NAME,
                self.YOUTUBE_API_VERSION,
                developerKey=self.DEVELOPER_KEY,
                cache_discovery=False)
            print("BUILD SUCCESS")
        except ServerNotFoundError:
            print("BUILD FAILED - NO INTERNET CONNECTION")
            sys.exit(0)

    def _get_search_short(self, text):
        aphanum = re.sub(r'\W+', '', text)
        return ''.join(aphanum)

    def _fetch_vars(self):
        config.read(CONFIG)
        self.TIME_DELTA = int(config.get("main", "default_time_crawler"))
        self.YOUTUBE_API_SERVICE_NAME = config.get("api", "youtube_api_service_name")
        self.YOUTUBE_API_VERSION = config.get("api", "youtube_api_version")
        self.KEYS_PATH = config.get("api", "keys_path")
        with open(self.KEYS_PATH, 'r+') as fp:
            self.codes = fp.readlines()

        # datapath
        self.video_search_files = config.get("datapath", "video_search_files")
        self.channel_search_files = config.get("datapath", "channel_search_files")
        self.video_data_files = config.get("datapath", "video_data_files")
        self.subtitle_subtitle_dir = config.get("datapath", "subtitle_subtitle_dir")

    def _try_next_id(self):
        """
        Update the API
        :return:
        """
        if self.code_index + 1 < len(self.codes):
            self.code_index += 1
            self.DEVELOPER_KEY = self.codes[self.code_index].strip()  # Update a new key
            self.youtube = build(
                self.YOUTUBE_API_SERVICE_NAME,
                self.YOUTUBE_API_VERSION,
                developerKey=self.DEVELOPER_KEY,
                cache_discovery=False)
            print(f"Update Developer Key:{self.DEVELOPER_KEY}")
        else:
            print("running out keys")
            sys.exit(0)
        self.DEVELOPER_KEY = self.codes[self.code_index].strip()  # Use your own Keys.

    def get_video(self, video_id):
        """
        Get one video by id
        :param video_id:
        :return:
        """
        part = "id,snippet,statistics,contentDetails"
        try:
            response = self.youtube.videos().list(part=part,
                                                  maxResults=1,
                                                  id=video_id).execute()
            if len(response["items"]) == 0:
                return "error"
            return response["items"][0]
        except HttpError as e:
            error = self._get_error_code(e.content)
            if error == "update_API_key":
                self._try_next_id()
                return self.get_video(video_id)
        except Exception as e:
            print(e)
            return "error"

    def get_comments(self, video_id, comment_page_count):
        """
        Save video comments of all the videos saved in {channel_list_dir}
        JSON returned from https://developers.google.com/youtube/v3/docs/comments
        :param video_id:
        :param comment_page_count:
        :return:
        """
        part = "snippet"
        try:
            response = self.youtube.commentThreads().list(part=part,
                                                          maxResults=100,
                                                          videoId=video_id).execute()
            comments = response["items"]
            counter = 0  # save the first page_count pages
            while "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = self.youtube.commentThreads().list(part=part,
                                                              maxResults=100,
                                                              videoId=video_id,
                                                              pageToken=page_token).execute()
                comments += response["items"]
                if counter == comment_page_count:
                    return comments
                counter += 1
            return comments
        except HttpError as e:
            error = self._get_error_code(e.content)
            if error == "update_API_key":
                self._try_next_id()
                return self.get_comments(video_id, comment_page_count)
        except Exception as e:
            return "error"

    def get_channel(self, channel_id):
        """
        # Save channel info of all the videos saved in {video_list_dir}
        :param channel_id:
        :return:
        """
        try:
            part = "id,snippet,statistics,contentDetails,topicDetails,brandingSettings,contentOwnerDetails," \
                   "localizations "
            response = self.youtube.channels().list(part=part, maxResults=1, id=channel_id).execute()
            return response["items"][0]
        except HttpError as e:
            error = self._get_error_code(e.content)
            if error == "update_API_key":
                self._try_next_id()
                return self.get_channel(channel_id)
        except Exception as e:
            return "error"

    def get_caption(self, video_id):
        """
        Save closed captions info of all the videos saved in {video_list_path}
        :param video_id:
        :return:
        """
        caption = []
        try:
            caption = YouTubeTranscriptApi.get_transcript(video_id)
            return caption
        except Exception as e:
            # print(e)
            return "error"

    def get_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except:
            return None

    def toDayFormat(self, date):
        return f"{date.month}-{date.day}-{date.year}"

    def isCrawled(self, file_name):
        return os.path.exists(file_name)

    def _write_item(self, file_path, items):
        with open(file_path, 'a+') as fp:
            for item in items:
                fp.write(json.dumps(item) + "\n")

    def _get_error_code(self, message):
        error = json.loads(message)
        reason = "unknown"
        if error["error"]["errors"][0]["reason"]:
            reason = error["error"]["errors"][0]["reason"]
        if reason == "dailyLimitExceeded" or reason == "quotaExceeded":
            print("Running out of quotas. Updating API key.")
            return "update_API_key"
        elif reason == 'badRequest':
            print("API deprecated. Delete API from key file.")
            return "update_API_key"
