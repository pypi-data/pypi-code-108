from .teamtv_object import TeamTVObject


class Video(TeamTVObject):
    @property
    def video_id(self):
        return self._video_id

    @property
    def parts(self):
        return self._parts

    @property
    def media_url(self):
        return self._media_url

    @property
    def state(self):
        return self._state

    def __repr__(self):
        return f"<Video video_id={self.video_id} state={self.state}>"

    def _use_attributes(self, attributes: dict):
        self._video_id = attributes['videoId']
        self._parts = attributes['parts']
        self._media_url = attributes.get('mediaUrl')
        self._state = attributes['state']
