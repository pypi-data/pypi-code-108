## Import and configuration
import json
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date
import pytz
import pandas as pd
from configparser import ConfigParser
import sys
import os
import math
from clarku_youtube_crawler.CrawlerObject import _CrawlerObject

CONFIG = "config.ini"
config = ConfigParser(allow_no_value=True)
config.read(CONFIG)


class RawCrawler(_CrawlerObject):
    def __init__(self):
        self.video_list_path = None
        super().__init__()

    def crawl(self, search_key, **kwargs):
        """
        Call this function to search a list of videos by {search _key}. Data will be saved to /video_search_list.
        One json contains search results on one day.
        :param search_key: The keywords to search YouTube. Supports general YouTube search methods including wildcards.
        :param kwargs: You can specify start_day, start_month, start_year, end_day, end_month, end_year, day_count
        :return: All search results saved in video_list/{search_key}. Each file contains all matched  videos on a specific day
        """
        self.search_key = search_key

        default = datetime.now() - timedelta(days=self.TIME_DELTA)
        start_day = kwargs.get("start_day", default.day)
        start_month = kwargs.get("start_month", default.month)
        start_year = kwargs.get("start_year", default.year)
        end_day = kwargs.get("end_day", None)
        end_month = kwargs.get("end_month", None)
        end_year = kwargs.get("end_year", None)
        day_count = kwargs.get("day_count", None)

        # day_count will be overwritten
        if end_day and end_month and end_year:
            start = date(start_year, start_month, start_day)
            end = date(end_year, end_month, end_day)
            delta_time = end - start
            day_count = int(delta_time.days)
        if not day_count:
            day_count = math.inf

        start_datetime = datetime(year=start_year, month=start_month, day=start_day, tzinfo=pytz.utc)
        date_mark = self.toDayFormat(start_datetime)
        delta = timedelta(hours=24)

        count = 0
        while count < day_count:
            print(f"start crawling:{date_mark}")
            # Initialize the paths
            video_file_name = f"{self._get_search_short(self.search_key)}~~{date_mark}_.json"
            self.video_list_path = f"{self.CURRENT_ROOT}{self.video_search_files}{video_file_name}"
            # crawl data, update start date.
            if not os.path.exists(self.video_list_path):
                self._crawl_data_one_day(start_datetime)
            else:
                print(f"Skip {self.video_list_path}. Date already crawled. ")
            start_datetime += delta
            date_mark = self.toDayFormat(start_datetime)
            count += 1

    def _crawl_data_one_day(self, start_datetime):
        """
        Add one day to the next crawl
        :param start_datetime:
        :return:
        """
        delta = timedelta(hours=24)
        print(f"crawling video list....")
        self._crawl_data(start_datetime, start_datetime + delta)

    def _crawl_data(self, start_time, end_time):
        """
        Iterate through all nextPageToken to get all available videos
        :param start_time: The beginning datetime
        :param end_time: The cutoff datetime
        :return:
        """
        response = self._search_data(self.video_list_path, start_time, end_time)
        total_result = response["pageInfo"]["totalResults"]
        if "nextPageToken" not in response:
            start_time_mark = self.toDayFormat(start_time)
            end_time_mark = self.toDayFormat(end_time)
            print(f"total results:{str(total_result)} between {start_time_mark} and {end_time_mark}")
            return
        while True:
            response = self._search_data(self.video_list_path, start_time, end_time, response["nextPageToken"])
            if "nextPageToken" not in response:
                start_time_mark = self.toDayFormat(start_time)
                end_time_mark = self.toDayFormat(end_time)
                print(f"total results:{str(total_result)} between {start_time_mark} and {end_time_mark}")
                break

    def _search_data(self, file_path, start_time, end_time, page_token=None):
        """
        Crawl a list of videos which matches {search_key}. Save the data in {video_list_dir}
        JSON returned from https://developers.google.com/youtube/v3/docs/search/list
        :param file_path: file path to save the collected video
        :param start_time: collect video from this date
        :param end_time: collect video to this date
        :param page_token: Do not modify this param
        :return:
        """
        part = "snippet"
        try:
            if page_token:
                response = self.youtube.search().list(part=part,
                                                      maxResults=50,
                                                      q=self.search_key,
                                                      pageToken=page_token,
                                                      type="video",
                                                      publishedAfter=start_time.isoformat(),
                                                      publishedBefore=end_time.isoformat(),
                                                      regionCode="US"
                                                      ).execute()
            else:
                response = self.youtube.search().list(part=part,
                                                      maxResults=50,
                                                      q=self.search_key,
                                                      type="video",
                                                      publishedAfter=start_time.isoformat(),
                                                      publishedBefore=end_time.isoformat(),
                                                      regionCode="US"
                                                      ).execute()
            self._write_item(file_path, response["items"])  # remove duplicate
            return response
        except HttpError as e:
            error = self._get_error_code(e.content)
            if error == "update_API_key":
                self._try_next_id()
                return self._search_data(file_path, start_time, end_time, page_token)
        except Exception as e:
            print(e)
            sys.exit(0)

    def merge_to_workfile(self, **kwargs):
        """
        This function merges videos on different days to a csv worklist. Later the crawler will use the worklist to collect
        all video data.
        Search results will be merged into video_to_collect.csv Unique identifiers: video id and search key
        :param kwargs:
        :param dirpath: the file of raw search
        :param destination: save to a csv work file containing all videos to be collected.
        You can change the video_search_list to other folders by setting file_dir={other search key}
        :return: this function will generates video_list.csv in YouTube_RAW folder
        """
        dirpath = kwargs.get("file_dir", f"{self.CURRENT_ROOT}{self.video_search_files}")
        destination = kwargs.get("destination", f"{self.CURRENT_ROOT}videos_to_collect.csv")

        video_list = []
        json_list = (file for file in os.listdir(dirpath) if file.endswith(".json"))
        # Save video meta data of all the videos saved in {video_list_path}
        for filename in json_list:
            with open(dirpath + filename, 'r') as fp:
                line = fp.readline()
                while line and line != "":
                    search_result = json.loads(line)
                    if "videoId" in search_result["id"]:
                        video_list.append({
                            "videoId": ":" + search_result["id"]["videoId"],
                            "channelId": search_result["snippet"]["channelId"],
                            "publishedAt": search_result["snippet"]["publishedAt"].split("T")[0],
                            "searchKey": filename.split("~~")[0],
                            "dateAdded": datetime.now()
                        })
                    line = fp.readline()

        df = pd.DataFrame(data=video_list)
        if os.path.exists(destination):
            tdf = pd.read_csv(destination)
            df = pd.concat([tdf, df])
            df = df.drop_duplicates(subset=["videoId", "searchKey"], keep='last')
            df.to_csv(destination, index=False)
            print(f"new videos added to work file {destination}")
        else:
            df.to_csv(destination, index=False)
            print(f"new work file created at {destination}")

    def crawl_videos_in_list(self, **kwargs):
        """
        Using video_list.csv to crawl further information. Crawled info documentation is in YouTube API.
        :keyword comment_page_count: default is in config: default_comment_page_count.
        :keyword search_key: which search key to use to crawl in video_list.csv.
        :keyword video_id: specify which column contains video ids (ids must append ":" before the actual id).
        :return: the result will be saved in YouTube_RAW/video_data/ with one json of one video
        """
        comment_page_count = kwargs.get("comment_page_count", config.get("main", "default_comment_page_count"))
        video_list_workfile = kwargs.get("video_list_workfile", f"{self.CURRENT_ROOT}videos_to_collect.csv")
        video_column = kwargs.get('video_id', 'videoId')
        video_data_dir = kwargs.get("video_data_dir", f"{self.CURRENT_ROOT}{self.video_data_files}")
        self.search_key = kwargs.get("search_key", self.search_key)
        df = pd.read_csv(video_list_workfile)
        crawl_count = 0

        # add filtering here
        for index, row in df.iterrows():
            video_id = row[video_column][1:]  # remove the ":" in the 1st char
            # channel_id = row["channelId"]
            filename = video_id + ".json"
            print(f"Crawling {filename}")
            if not self.isCrawled(f"{video_data_dir}/" + filename):
                video = self.get_video(video_id)
                if video != 'error':
                    channel_id = video['snippet']['channelId']
                    comments = self.get_comments(video_id, comment_page_count)
                    channel = self.get_channel(channel_id)
                    caption = self.get_caption(video_id)
                    result = {
                        "videoId": video_id,
                        "channelId": channel_id,
                        "video": video,
                        "comments": comments,
                        "channel": channel,
                        "caption": caption,
                        "searchKey": row['searchKey'] if "searchKey" in row else "",
                    }
                    try:
                        os.mkdir(f"{video_data_dir}/")
                    except OSError:
                        pass
                    with open(f"{video_data_dir}/" + filename, 'w+') as fp:
                        fp.write(json.dumps(result) + "\n")
                    crawl_count += 1
                else:
                    print(f'error crawling {video_id}')
            else:
                print(f"Skip {video_id}, already crawled in {video_data_dir}")

    def merge_all(self, **kwargs):
        """
        merge all collected JSONs from video_data to one file.
        :param kwargs: you can specify the source JSON folder by configure  directory={your own dir}
        you can specify the name of merged file by configure save_to={your file name}
        :return:
        """

        # search_key is either None, or a list of search keys
        video_data_directory = kwargs.get("directory", f"{self.CURRENT_ROOT}{self.video_data_files}")
        save_to = kwargs.get("save_to", f"{self.CURRENT_ROOT}all_videos.json")

        # handling finding directories
        if not os.path.isdir(video_data_directory):
            raise FileNotFoundError(f"can't find {video_data_directory}")
        else:
            self._merge_for_dirlist(video_data_directory, save_to)

    def _merge_for_dirlist(self, directory, save_to):
        json_list_dir = [file for file in os.listdir(directory) if file.endswith(".json")]
        with open(save_to, 'w+') as video_writer:
            for filename in json_list_dir:
                with open(directory + filename, 'r') as fp:
                    line = fp.readline()
                    while line and line != "":
                        video_writer.write(line)
                        line = fp.readline()
