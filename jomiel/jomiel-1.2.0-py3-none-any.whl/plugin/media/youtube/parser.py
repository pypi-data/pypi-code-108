#
# jomiel
#
# Copyright
#  2019-2021 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from json import loads
from re import match as re_match
from urllib.parse import parse_qs
from urllib.parse import urlencode

from jomiel.error import ParseError
from jomiel.hypertext import http_get
from jomiel.hypertext import http_post
from jomiel.log import lg
from jomiel.plugin.media.parser import PluginMediaParser
from requests.exceptions import HTTPError

# from jomiel_kore.formatter import json_pprint


class Parser(PluginMediaParser):
    """Media metadata parser implementation for YouTube.

    - Retrieve data from the /get_video_info endpoint
    - If that fails, try the /youtubei/player endpoint, instead.

    """

    __slots__ = []

    def __init__(self, uri_components):
        """Initializes the object.

        Args:
            uri_components (dict): The input URI components

        """
        super().__init__(uri_components)
        self.parse(uri_components)

    def parse(self, uri_components):
        """Parses the relevant metadata for the media.

        Args:
            uri_components (dict): The input URI components

        Raises:
            jomiel.error.ParseError if a parsing error occurred

        """

        def _parse_metadata(video_info):
            """Parse meta data from the video info."""

            def _value_from(d, key_name):
                """Return value from a dictionary, or raise an error."""
                if key_name in d:
                    return d.get(key_name)
                raise ParseError(f"'{key_name}' not found")

            def _check_playability_status():
                """Check the 'playability status' of the video."""
                playability_status = _value_from(
                    video_info,
                    "playabilityStatus",
                )
                if playability_status["status"] == "ERROR":
                    raise ParseError(playability_status["reason"])

            def _parse_video_details():
                """Return video details."""

                def _int(key_name):
                    """Return int from 'vd' or 0."""
                    value = vd.get(key_name, 0)
                    return int(value)

                def _float(key_name):
                    """Return float from 'vd' or 0."""
                    value = vd.get(key_name, 0)
                    return float(value)

                def _str(key_name):
                    """Return str from 'vd' or ''."""
                    return vd.get(key_name, "")

                vd = _value_from(video_info, "videoDetails")

                self.media.statistics.average_rating = _float(
                    "averageRating",
                )

                self.media.statistics.view_count = _int("viewCount")
                self.media.length_seconds = _int("lengthSeconds")

                self.media.description = _str("shortDescription")
                self.media.author.channel_id = _str("channelId")

                self.media.author.name = _str("author")
                self.media.title = _str("title")

                thumbnail = vd.get("thumbnail")
                if thumbnail:
                    thumbnails = thumbnail.get("thumbnails", [])
                    # Re-use 'vd' so that _int() works out of the box.
                    for vd in thumbnails:
                        thumb = self.media.thumbnail.add()
                        thumb.width = _int("width")
                        thumb.height = _int("height")
                        thumb.uri = vd["url"]

            def _parse_streaming_data():
                """Parse 'streaming data'."""

                def _parse(key_name):
                    """Parse an element of the 'streaming data'."""

                    def _parse_format():
                        """Parse 'format' of streaming data."""

                        def _profile():
                            """Generate the stream profile string."""
                            profile = _fmt.get(
                                "qualityLabel",
                                _fmt.get("quality", "undefined"),
                            )
                            return f"{profile} (itag={_fmt['itag']})"

                        def _int(key_name):
                            """Return int from '_fmt' dict or 0."""
                            value = _fmt.get(key_name, 0)
                            return int(value)

                        stream = self.media.stream.add()

                        stream.content_length = _int("contentLength")
                        stream.quality.bitrate = _int("bitrate")

                        stream.quality.height = _int("height")
                        stream.quality.width = _int("width")

                        stream.quality.profile = _profile()
                        stream.mime_type = _fmt["mimeType"]

                        stream.uri = _fmt["url"]

                    for _fmt in streaming_data[key_name]:
                        _parse_format()

                streaming_data = _value_from(
                    video_info,
                    "streamingData",
                )
                _parse("adaptiveFormats")
                _parse("formats")

            # json_pprint(video_info)
            _check_playability_status()
            _parse_video_details()
            _parse_streaming_data()

        def _parse_player_response():
            """Return 'player_response'."""
            if "player_response" in video_info:
                pr = video_info["player_response"]
                if isinstance(pr, list):
                    if len(pr) > 0:
                        return pr[0]
                    raise ParseError("'player_response' is empty")
                raise ParseError("'player_response' is not 'list'")
            raise ParseError("'player_response' not found")

        def _parse_video_id():
            """Return video identifier."""
            result = re_match(r"v=([\w\-_]{11})", uri_components.query)
            if not result:
                raise ParseError("unable to match video ID")
            self.media.identifier = result.group(1)

        def _video_info_request():
            """Make a GET request to the /get_video_info endpoint."""
            v_id = self.media.identifier
            data = urlencode(
                {
                    "video_id": v_id,
                    "eurl": f"https://youtube.googleapis.com/v/{v_id}",
                    "html5": 1,
                    "c": "TVHTML5",
                    "cver": "6.20180913",
                },
            )
            uri = f"https://www.youtube.com/get_video_info?{data}"
            return http_get(uri).text

        def _youtubei_player_request():
            """Make a POST request to the /youtubei/player endpoint."""
            uri = "https://www.youtube.com/youtubei/v1/player"
            params = {"key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"}
            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20201021.03.00",
                    },
                },
            }
            payload.update({"videoId": self.media.identifier})
            return http_post(uri, payload, params=params).text

        _parse_video_id()
        try:
            video_info = _video_info_request()
            video_info = parse_qs(video_info)
            video_info = _parse_player_response()
        except HTTPError:
            # /get_video_info endpoint failed. Try /youtubei/player.
            lg().debug("http<get>: /get_video_info failed")
            video_info = _youtubei_player_request()
        json = loads(video_info)
        _parse_metadata(json)


# vim: set ts=4 sw=4 tw=72 expandtab:
