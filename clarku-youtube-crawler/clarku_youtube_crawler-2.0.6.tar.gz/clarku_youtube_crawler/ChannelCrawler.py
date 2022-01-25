## Import and configuration
import json
import os
from configparser import ConfigParser
import pandas as pd
from googleapiclient.errors import HttpError

from clarku_youtube_crawler.CrawlerObject import _CrawlerObject

CONFIG = "config.ini"
config = ConfigParser(allow_no_value=True)
config.read(CONFIG)


class ChannelCrawler(_CrawlerObject):
    def __init__(self):
        super().__init__()

    def search_channel(self, search_key):
        self.search_key = search_key
        search_key_dir = f"{self.CURRENT_ROOT}{self.channel_search_files}{self.search_key}.json"
        if os.path.exists(search_key_dir):
            os.remove(search_key_dir)
        self._crawl_channels(search_key_dir)

    def _crawl_channels(self, file_path):
        response = self._search_channel(file_path=file_path)
        print("debug", response)
        if response != "error":
            total_result = response["pageInfo"]["totalResults"]
            if "nextPageToken" not in response:
                print(f"total results:{str(total_result)}")
                return
            while True:
                response = self._search_channel(file_path=file_path,
                                                page_token=response["nextPageToken"])
                if "nextPageToken" not in response:
                    print(f"total results:{str(total_result)}")
                    break

    def _search_channel(self, file_path, page_token=None):
        """
        Crawl a list of videos which matches {search_key}. Save the data in {video_list_dir}
        JSON returned from https://developers.google.com/youtube/v3/docs/search/list
        :param file_path: file to save the returned json
        :param page_token: A page token to start with
        :return: success or error message
        """
        part = "snippet"
        try:
            if page_token:
                response = self.youtube.search().list(part=part,
                                                      maxResults=50,
                                                      q=self.search_key,
                                                      pageToken=page_token,
                                                      type="channel",
                                                      regionCode="US"
                                                      ).execute()
            else:
                response = self.youtube.search().list(part=part,
                                                      maxResults=50,
                                                      q=self.search_key,
                                                      type="channel",
                                                      regionCode="US"
                                                      ).execute()
            self._write_item(file_path, response["items"])  # remove duplicate
            return response
        except HttpError as e:
            error = self._get_error_code(e.content)
            if error == "update_API_key":
                self._try_next_id()
                return self._search_channel(file_path, page_token)
        except Exception as e:
            print(e)
            return "error"

    def merge_to_workfile(self, **kwargs):
        """
        Process videos in video_list,
        :param kwargs: You can change the search_key by setting file_dir={other search key}. It will visit corresponding
        folders in YouTube_RAW/video_list/{search_key}. If this new search key is not specified,
        the key used to retrieve search results will be used.
        :return: this function will generates video_list.csv in YouTube_RAW folder
        """
        dirpath = kwargs.get("file_dir", f"{self.CURRENT_ROOT}{self.channel_search_files}")
        destination = kwargs.get("destination", f"{self.CURRENT_ROOT}channels_to_collect.csv")

        json_list = [file for file in os.listdir(dirpath) if file.endswith(".json")]

        channel_list = []
        for jsonFile in json_list:
            with open(dirpath + "/" + jsonFile, 'r') as fp:
                lines = fp.readlines()
            for line in lines:
                channel_json = json.loads(line)
                dataObj = {
                    "channelId": channel_json["snippet"]["channelId"],
                    "publishedAt": channel_json["snippet"]["publishedAt"].split("T")[0],
                    "channelName": channel_json["snippet"]["channelTitle"],
                    "homePage": f"https://www.youtube.com/channel/{channel_json['snippet']['channelId']}",
                    "searchKey": jsonFile,
                    "description": channel_json["snippet"]["description"],
                }
                channel_list.append(dataObj)

            df = pd.DataFrame(data=channel_list)
            df.to_csv(destination, index=False)

    def crawl(self, **kwargs):
        """
        crawl all videos belong to a list of channels (specified by channelIds)
        :param kwargs: specify channel_header to configure which column contains channel id
        :return:
        """
        filename = kwargs.get("filename", f"{self.CURRENT_ROOT}channels_to_collect.csv")
        header = kwargs.get("channel_header", "channelId")
        search_key_subdir = kwargs.get("save_to", f"{self.CURRENT_ROOT}{self.video_search_files}")
        accepted_ext = [".csv", ".xlsx"]

        file, ext = os.path.splitext(filename)
        if ext not in accepted_ext:
            raise ValueError(f"{ext} is not an accepted file type")

        if ext == ".csv":
            df = pd.read_csv(filename)
        elif ext == ".xlsx":
            df = pd.read_excel(filename)
        self.channel_list = set(df[header])

        try:
            os.mkdir(search_key_subdir)
        except OSError:
            print("Directory already exists %s" % search_key_subdir)
        else:
            print("Successfully created the directory %s " % search_key_subdir)

        for channelId in self.channel_list:
            dir = f"{search_key_subdir}/{channelId}.json"
            if not self.isCrawled(dir):
                print(f"Crawling a video list from {channelId}....")
                self._search_videos_from_channels(dir, channelId)
            else:
                print(f"Skip {channelId}, channel already crawled")

    def _search_videos_from_channels(self, file_name, channel_id):
        response = self._search_all_videos_in_channel(file_name, channel_id)
        total_results = response["pageInfo"]["totalResults"]
        print(f"Total videos: {total_results}")
        while response is not None and "nextPageToken" in response:
            response = self._search_all_videos_in_channel(file_name, channel_id, response["nextPageToken"])

    def _search_all_videos_in_channel(self, file_path, channel_id, page_token=None):
        """
        Get all videos of a channel
        :param file_path: the directory to save the returned json
        :param channel_id:
        :param page_token:
        :return:
        """
        part = "snippet"
        try:
            if page_token:
                response = self.youtube.search().list(part=part,
                                                      maxResults=50,
                                                      pageToken=page_token,
                                                      type="video",
                                                      channelId=channel_id,
                                                      regionCode="US"
                                                      ).execute()
            else:
                response = self.youtube.search().list(part=part,
                                                      maxResults=50,
                                                      type="video",
                                                      channelId=channel_id,
                                                      regionCode="US"
                                                      ).execute()
            self._write_item(file_path, response["items"])
            return response
        except HttpError as e:
            error = self._get_error_code(e.content)
            if error == "update_API_key":
                self._try_next_id()
                return self._search_all_videos_in_channel(file_path, channel_id,
                                                          page_token)  # I assume it's missing one var
        except Exception as e:
            print(e)
            return "error"
