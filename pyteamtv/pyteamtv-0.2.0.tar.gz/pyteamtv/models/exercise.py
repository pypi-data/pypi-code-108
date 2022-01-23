from dataclasses import dataclass
from typing import List

from .teamtv_object import TeamTVObject

@dataclass
class File(object):
    filename: str
    size: int

class Exercise(TeamTVObject):
    @property
    def title(self):
        return self._title

    @property
    def exercise_id(self):
        return self._exercise_id

    @property
    def video_id(self):
        return self._video_id

    @property
    def tags(self):
        return self._tags

    def init_video_upload(self, files: List[File]):
        # TODO: make sure we can return a partial video object
        video_id = self._requester.request(
            "POST",
            f"/exercises/{self.exercise_id}/initVideoUpload",
            dict(
                files=[dict(filename=file.filename, size=file.size) for file in files]
            )
        )
        self._video_id = video_id
        return video_id

    def set_variables(self, variables: dict):
        self._requester.request(
            "POST",
            f"/exercises/{self.exercise_id}/setVariables",
            dict(
                variables=variables
            )
        )

    def __repr__(self):
        return f'<Exercise exercise_id={self.exercise_id} title="{self.title}" video_id={self.video_id}>'

    def _use_attributes(self, attributes: dict):
        self._exercise_id = attributes['exerciseId']
        self._title = attributes['title']
        self._video_id = attributes.get('videoId')
        self._tags = attributes.get('tags', {})
