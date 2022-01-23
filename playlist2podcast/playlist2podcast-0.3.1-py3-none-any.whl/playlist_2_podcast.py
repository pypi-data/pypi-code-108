"""Main / Overall logic for downloading videos of a Youtube playlist,
converting to MP3 and creating a podcast ATOM feed.

playlist2podcast - create podcast feed from a playlist URL
Copyright (C) 2021 - 2022  Mark S Burgunder

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import argparse
import datetime
import json
import logging
import os
import re
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import arrow
import httpx
import youtube_dl
from feedgen.feed import FeedGenerator
from PIL import Image
from rich import print as rprint
from rich import traceback
from rich.logging import RichHandler

from playlist2podcast import __version__
from playlist2podcast import CODE_VERSION_MAJOR
from playlist2podcast import CODE_VERSION_MINOR
from playlist2podcast import CODE_VERSION_PATCH

traceback.install(show_locals=True)


YDL_DL_OPTS = {
    "quiet": "true",
    "ignoreerrors": "true",
    "logger": logging.getLogger("Youtube_dl"),
    "format": "bestaudio/best",
    "outtmpl": "publish/media/%(id)s.%(ext)s",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
        }
    ],
}


# pylint: disable=too-many-instance-attributes
@dataclass
class Configuration:
    """Dataclass containing all configuration parameters needed to run
    Playlist2Podcast The init method will load the values from a config files
    if it exists.

    If the configuration file does not exist the init method will
    interactively ask the user for all required parameters and then save
    these in the configuration file for subsequent executions.
    """

    version: str
    play_lists: List[Dict[str, Union[str, List[str]]]]
    publish_dir: str
    media_dir: str
    podcast_host: str
    number_of_episodes: int
    log_level: str
    youtube_cookie_file: Optional[str]

    def __init__(self, config_file_name: str) -> None:

        if os.path.exists(config_file_name):
            with open(file=config_file_name, encoding="UTF-8") as config_file:
                config = json.load(config_file)
        else:
            config = {}
        self.version = config.get("version", None)

        # Migrate old play list config to new style config
        if not self.version:
            previous_play_lists = config.get("play_list", [])
            self.play_lists = [
                {"url": current_list, "include": [], "exclude": []}
                for current_list in previous_play_lists
            ]
        else:
            self.play_lists = config.get("play_lists", [])

        self.publish_dir = config.get("publish_dir", None)
        self.media_dir = config.get("media_dir", None)
        self.podcast_host = config.get("podcast_host", None)
        self.number_of_episodes = config.get("number_of_episodes", None)
        self.log_level = config.get("log_level", "INFO")
        self.youtube_cookie_file = config.get("youtube_cookie_file", None)

        if len(self.play_lists) == 0:
            self.__collect_playlists_info()

        if not self.publish_dir:
            rprint(
                "Enter the name of the directory to place all the generated files into."
            )
            rprint("This directory will be created if needed")
            self.publish_dir = input("[...] Local podcast directory: ")

        if not self.media_dir:
            rprint(
                "Enter the name of the directory to hold all the media files, "
                "such as audio files and thumbnail images."
            )
            self.media_dir = input(
                "[...] Directory to hold generated podcast media files: "
            )

        if not self.podcast_host:
            rprint(
                "Enter the url stub of where you will be hosting the "
                "generated podcast files"
            )
            self.podcast_host = input("[...] Podcast Host URL: ")

        if not self.number_of_episodes:
            rprint(
                "Enter the number of episodes to process from Youtube playlist and "
                "process into the generated podcast feed"
            )
            self.number_of_episodes = int(
                input("[...] Number of episodes to include: ")
            )

        if self.youtube_cookie_file is None:
            rprint("Enter path and filename for the file containing a youtube cookie.")
            rprint("Leave empty if no cookie file is needed")
            self.youtube_cookie_file = input("[...] full path and file name: ")

        self.version = __version__
        with open(file=config_file_name, mode="w", encoding="UTF-8") as config_file:
            json.dump(asdict(self), config_file, indent=4)

    def __collect_playlists_info(self) -> None:
        """Prompts user to enter playlist urls and any associated
        include/exclude filters."""
        self.play_lists = []
        while True:
            rprint(
                "Enter the url of a video playlist."
                'Once you have added the last playlist url enter a "." '
                "(single full stop by itself) to proceed."
            )
            entered_play_list = input("[...] Playlist URL: ")

            if entered_play_list == ".":
                break

            # Collect include filters
            rprint(
                "Enter any include or exclude filter(s) to determine if a video "
                "should be included or skipped. These filters should be regular "
                "expressions. (Check out https://regex101.com/ to create and/or "
                "debug regular expressions.)/n"
                "We will start with include filter(s) one at a time. Leave filter "
                "entry blank to finish adding include and then exclude filters."
            )
            entered_include_filters = []
            while True:
                include = input("[...] Enter an include filter (if applicable): ")
                if include:
                    entered_include_filters.append(include)
                else:
                    break

            # Collect exclude filters
            rprint(
                "Next, enter any exclude filter(s). Again, leave the filter "
                "entry blank to finish adding exclude filters."
            )
            entered_exclude_filters = []
            while True:
                exclude = input("[...] Enter an exclude filter (if applicable): ")
                if exclude:
                    entered_exclude_filters.append(exclude)
                else:
                    break

            self.play_lists.append(
                {
                    "url": entered_play_list,
                    "include": entered_include_filters,
                    "exclude": entered_exclude_filters,
                }
            )


def main() -> None:
    """Main / Overall Logic of Youtube Playlist to podcast feed conversion.

    :param: None
    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Create Podcast feed from Youtube Playlist."
    )
    parser.add_argument(
        "-c", "--config-file", action="store", default="config.json", dest="config_file"
    )
    args = parser.parse_args()

    config = Configuration(config_file_name=args.config_file)

    logger = logging.getLogger("VideoPlaylist2Podcast")
    logger.setLevel(logging.DEBUG)

    std_out_formatter = logging.Formatter(
        "%(name)s[%(process)d] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    std_out_handler = RichHandler()
    std_out_handler.setFormatter(std_out_formatter)
    std_out_handler.setLevel(config.log_level)
    logger.addHandler(std_out_handler)

    check_updates(logger)

    feed = FeedGenerator()
    feed.author(name="Marvin", email="marvin@example.com")
    feed.link(href=f"{config.podcast_host}/feed.rss", rel="alternate")
    feed.load_extension("podcast")
    feed.title("Marvin's Youtube Playlist Podcast")
    feed.description("Marvin's Youtube Playlist Podcast")

    download_options = YDL_DL_OPTS
    if config.youtube_cookie_file and config.youtube_cookie_file != "":
        download_options["cookiefile"] = config.youtube_cookie_file
    downloader = youtube_dl.YoutubeDL(download_options)

    for current_play_list in config.play_lists:
        logger.info(
            "Downloading info for videos on playlist: %s", current_play_list["url"]
        )
        videos_list = downloader.extract_info(current_play_list["url"], download=False)[
            "entries"
        ]

        videos_to_download = [
            video
            for video in videos_list
            if video
            and is_video_included(
                video["title"],
                cast(List[str], current_play_list["include"]),
                cast(List[str], current_play_list["exclude"]),
                logger,
            )
        ]

        add_episodes(config, downloader, feed, logger, videos_to_download)

    feed.rss_file(
        f"{config.publish_dir}/feed.rss",
        extensions=True,
        pretty=True,
        xml_declaration=True,
    )


def is_video_included(
    video_title: str,
    include_filters: List[str],
    exclude_filters: List[str],
    logger: logging.Logger,
) -> bool:
    """Checks video title against include and exclude filters to determine if
    video should be considered for adding to podcast or not.

    :param video_title: Title of video to check filters against.
    :param include_filters: List of regex patterns acting as include filters.
        If one include filter matches, video will be considered for adding.
    :param exclude_filters: Lost of regex patterns actins as exclude filters.
        If one exclude filter matches, video will be skipped, even if there is a
        matching include filter. I.e. exclude > include
    :param logger: Logger to show progress on screen
    :return: True if video should be considered for adding and False if video should
        be skipped based on filters.
    """
    logger.debug(f"Filter checking video: {video_title}")

    should_include_video = False

    if len(include_filters) == 0:
        should_include_video = True

    else:
        for include_filter in include_filters:
            regex = re.compile(include_filter)
            if regex.match(video_title):
                logger.debug(
                    f"Include filter '{include_filter}' matches ... "
                    f"considering: {video_title}"
                )
                should_include_video = True

    if len(exclude_filters) > 0:
        for exclude_filter in exclude_filters:
            regex = re.compile(exclude_filter)
            if regex.match(video_title):
                logger.debug(
                    f"Exclude filter '{exclude_filter}' matches ... "
                    f"skipping: {video_title}"
                )
                should_include_video = False
                break

    return should_include_video


def add_episodes(
    config: Configuration,
    downloader: youtube_dl.YoutubeDL,
    feed: FeedGenerator,
    logger: logging.Logger,
    play_list_info: List[Dict[str, str]],
) -> None:
    """Iterates through play list info and decides which videos to process and
    add to feed and then does so.

    :param config: Contains program configuration
    :param downloader: Youtube-dl object to download and process videos
    :param feed: RSS feed to add episodes to
    :param logger: Logger to show progress on screen
    :param play_list_info: List of info dicts for each video in the playlist
    :return: None
    """
    ids_in_feed = {entry.id() for entry in feed.entry()}
    number_episodes_added = 0
    for video in play_list_info:
        if number_episodes_added < config.number_of_episodes:
            published_on = arrow.get(video["upload_date"], "YYYYMMDD")
            feed_entry = feed.add_entry()

            feed_entry.author(name=video["uploader"])
            feed_entry.id(video["id"])
            feed_entry.link(href=video["webpage_url"])
            feed_entry.title(video["title"])
            feed_entry.description(video["description"])
            feed_entry.published(published_on.datetime)

            # Download video if needed
            local_audio_file = (
                f"{config.publish_dir}/{config.media_dir}/{feed_entry.id()}.opus"
            )
            host_audio_file = (
                f"{config.podcast_host}/{config.media_dir}/{feed_entry.id()}.opus"
            )
            if not os.path.isfile(local_audio_file):
                logger.info(
                    "Downloading episode with id %s and length %s uploaded on %s with "
                    "title %s ",
                    feed_entry.id(),
                    datetime.timedelta(seconds=int(video["duration"])),
                    feed_entry.published().strftime("%Y-%m-%d"),
                    feed_entry.title(),
                )
                downloader.download([video["webpage_url"]])
            feed_entry.enclosure(host_audio_file, 0, "audio/ogg")

            thumbnail = get_thumbnail(config, feed_entry.id(), video)
            # pylint: disable=no-member
            feed_entry.podcast.itunes_image(
                f"{config.podcast_host}/{config.media_dir}/{thumbnail}"
            )
            feed_entry.podcast.itunes_duration(int(video["duration"]))

            number_episodes_added += 1
            ids_in_feed.add(feed_entry.id())

            logger.debug(
                "Added episode with id %s from %s with title %s",
                feed_entry.id(),
                feed_entry.published().strftime("%Y-%m-%d"),
                feed_entry.title(),
            )

        else:
            # Nothing to be done if episode / video has already been added to the feed
            if video["id"] in ids_in_feed:
                continue

            try:
                os.remove(f'{config.publish_dir}/{config.media_dir}/{video["id"]}.opus')
                os.remove(f'{config.publish_dir}/{config.media_dir}/{video["id"]}.jpg')
                logger.info(
                    "Removed old files for episode with id %s from %s with title %s",
                    video["id"],
                    video["upload_date"],
                    video["title"],
                )
            except FileNotFoundError:
                logger.debug(
                    "Skipping episode with id %s from %s with title %s",
                    video["id"],
                    video["upload_date"],
                    video["title"],
                )


def get_thumbnail(config: Configuration, video_id: str, video: Dict[str, Any]) -> str:
    """Gets the highest quality thumbnail out of the video dict, converts it to
    JPG and returns the filename of the converted file.

    :param config: Configuration class instance
    :param video_id: Youtube video id
    :param video: youtube-dl information dict about one particular video

    :return:  Filename of the converted Thumbnail
    """
    image_url = video["thumbnails"][-1]["url"]
    image_type = image_url.split(".")[-1]
    local_image = f"{config.publish_dir}/{video_id}.{image_type}"
    publish_image = f"{video_id}.jpg"
    publish_image_path = f"{config.publish_dir}/{config.media_dir}/{publish_image}"
    if not os.path.isfile(publish_image_path):
        remote_image = httpx.get(image_url)
        with open(local_image, "wb") as file:
            file.write(remote_image.content)
        thumbnail_wip = Image.open(local_image)
        thumbnail_wip.save(publish_image_path)
        os.remove(local_image)
    return publish_image


def check_updates(logger: logging.Logger) -> None:
    """Check of there is a newer version of MastodonAmnesia available on
    gitlab.

    :param logger: Logger object to be able to send message to log
    :return: None
    """
    try:
        response = httpx.get(
            "https://codeberg.org/PyYtTools/Playlist2Podcasts"
            "/raw/branch/main/update-check/release-version.txt"
        )
        response.raise_for_status()
        repo_version = response.content.decode("utf-8").strip().partition(".")
        repo_version_major = int(repo_version[0].strip())
        repo_minor_version_to_check = repo_version[2].strip().partition(".")
        repo_version_minor = int(repo_minor_version_to_check[0].strip())
        repo_version_patch = int(repo_minor_version_to_check[2].strip())

        code_version_numeric = CODE_VERSION_MAJOR * 1000000
        code_version_numeric += CODE_VERSION_MINOR * 1000
        code_version_numeric += CODE_VERSION_PATCH
        repo_version_numeric = repo_version_major * 1000000
        repo_version_numeric += repo_version_minor * 1000
        repo_version_numeric += repo_version_patch

        if code_version_numeric >= repo_version_numeric:
            logger.info(
                f"Playlist2Podcast v{CODE_VERSION_MAJOR}."
                f"{CODE_VERSION_MINOR}.{CODE_VERSION_PATCH} is up to date."
            )
        else:
            logger.warning(
                f"New version of Playlist2Podcast"
                f" (v{repo_version_major}.{repo_version_minor}.{repo_version_patch})"
                f" is available!"
            )
            logger.warning(
                f"(You have v{CODE_VERSION_MAJOR}."
                f"{CODE_VERSION_MINOR}.{CODE_VERSION_PATCH})"
            )
            logger.warning(
                "Latest available at: https://codeberg.org/PyYtTools/Playlist2Podcasts"
            )
    except (httpx.ConnectError, httpx.HTTPError) as update_check_error:
        logger.warning(
            "Encountered error while checking for updates: %s", update_check_error
        )


if __name__ == "__main__":
    main()
