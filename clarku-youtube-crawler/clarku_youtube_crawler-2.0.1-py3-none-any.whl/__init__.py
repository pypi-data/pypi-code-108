from configparser import ConfigParser
from datetime import date
import os

# You can configure here or in the generated config.ini file
# If you configure directly in this code, make sure to delete existing config.ini to reflect the changes
__all__ = ['RawCrawler', 'ChannelCrawler', 'JSONDecoder', 'SubtitleCrawler']
__version__ = '2.0.1'

CONFIG = "config.ini"
# DATE = str(date.today()).replace("-", "")  # today in yyyymmdd
# RAW_PARENT_PATH = f"YouTube_RAW/"
# CHANNEL_PARENT_PATH = f"YouTube_CHANNEL/"
# SUBTITLE_PARENT_PATH=f"YouTube_SUBTITLE/"

global OVERRIDE_CONFIG
OVERRIDE_CONFIG = False


def config_override(bool):
    global OVERRIDE_CONFIG
    OVERRIDE_CONFIG = bool
    if OVERRIDE_CONFIG or (not OVERRIDE_CONFIG and os.path.exists(CONFIG)):
        generate_config()


def generate_config():
    if os.path.exists(CONFIG):
        os.remove(CONFIG)
    main = {
        "default_time_crawler": "7",  # if no start date for crawl, go back this many days from today
        "default_subscriber_cutoff": "10000",
        "default_comment_page_count": "4",
    }

    datapath = {
        "video_search_files": f"video_search_list/",
        "channel_search_files": f"channel_search_list/",
        "video_data_files": "video_data/",
        "subtitle_subtitle_dir": f"subtitles/"
    }

    api = {
        "KEYS_PATH": "DEVELOPER_KEY.txt",
        "YOUTUBE_API_SERVICE_NAME": "youtube",
        "YOUTUBE_API_VERSION": "v3",
        "YOUTUBE_URL": "https://www.googleapis.com/youtube/v3/"
    }

    config = ConfigParser(allow_no_value=True)
    config.read(CONFIG)

    config.add_section('main')
    config.set('main', '; default_time_crawler: if no start date for crawl, go back this many days from today')
    for k, v in main.items():
        config.set("main", k, v)

    config.add_section('datapath')
    config.set('datapath', '; all sub directories in this section will be under RAW_PARENT_PATH')
    for k, v in datapath.items():
        config.set("datapath", k, v)

    config.add_section('api')
    for k, v in api.items():
        config.set("api", k, v)

    with open(CONFIG, 'w') as f:
        config.write(f)


if not os.path.exists(CONFIG):
    generate_config()

from clarku_youtube_crawler.ChannelCrawler import ChannelCrawler
from clarku_youtube_crawler.RawCrawler import RawCrawler
from clarku_youtube_crawler.JSONDecoder import JSONDecoder
from clarku_youtube_crawler.SubtitleCrawler import SubtitleCrawler
