import logging
import os
from datetime import datetime
from typing import Optional

from .list import List
from .observation import Observation
from .observation_log import ObservationLog
from .teamtv_object import TeamTVObject
from .video import Video

from tusclient.uploader import Uploader

class SportingEvent(TeamTVObject):
    @property
    def scheduled_at(self) -> datetime:
        return self._scheduled_at

    @property
    def sporting_event_id(self) -> str:
        return self._sporting_event_id

    @property
    def name(self):
        return self._name

    @property
    def tags(self):
        return self._tags

    @property
    def main_video_id(self) -> Optional[str]:
        if self._video_ids:
            return self._video_ids[0]
        return None

    @property
    def is_local(self):
        return self._is_local

    def get_observation_log(self) -> ObservationLog:
        video_id = self.main_video_id
        if video_id:
            clock_id = self._clocks[video_id]['clockId']
        else:
            clock_id = 'U1'

        return ObservationLog(
            Observation,
            self._requester,
            "GET",
            f"/sportingEvents/{self.sporting_event_id}/observations/{clock_id}",
            clock_id,
            self
        )

    def get_videos(self) -> List[Video]:
        def _filter(video: Video) -> bool:
            return video.video_id in self._video_ids

        return List(
            Video,
            self._requester,
            "GET",
            "/videos",
            item_filter=_filter
        )

    def upload_video(self, *file_paths: str) -> Video:
        files = []
        for filename in file_paths:
            files.append({
                'name': os.path.basename(filename),
                'size': os.path.getsize(filename)
            })

        video_id = self._requester.request(
            "POST",
            f"/sportingEvents/{self.sporting_event_id}/initVideoUpload",
            {
                "files": files
            }
        )

        video = Video(
            self._requester,
            self._requester.request(
                "GET",
                f"/videos/{video_id}"
            )
        )
        for i, part in enumerate(video.parts):
            uploader = Uploader(
                file_paths[i],
                url=part['tusUploadUrl'],
                chunk_size=25 * 1024 * 1024,
                log_func=lambda msg: logging.info(f"Uploading: {msg}"),

                retries=5,
                retry_delay=5
            )

            uploader.upload()

        return Video(
            self._requester,
            self._requester.request(
                "GET",
                f"/videos/{video_id}"
            )
        )

    def _use_attributes(self, attributes: dict):
        self._name = attributes['name']
        self._sporting_event_id = attributes['sportingEventId']
        self._tags = attributes.get('tags', {})
        self._video_ids = attributes.get('videoIds', [])
        self._clocks = attributes['clocks']
        self._scheduled_at = datetime.fromisoformat(attributes['scheduledAt'].replace("Z", "+00:00"))
        self._is_local = attributes['_metadata']['source']['type'] == 'ResourceGroup'

    def __str__(self):
        return f"{self._scheduled_at.strftime('%d/%m/%y')} {self._name}"
