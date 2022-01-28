from dataclasses import dataclass, field
from typing import List, Mapping, Union

from annotell.input_api.model.input.abstract.sequence_frame import SequenceFrame
from annotell.input_api.model.input.resources import Image, VideoFrame


@dataclass
class Frame(SequenceFrame):
    images: List[Image] = field(default_factory=list)
    video_frames: List[VideoFrame] = field(default_factory=list)
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(
            frameId=self.frame_id,
            relativeTimestamp=self.relative_timestamp,
            images=[image.to_dict() for image in self.images] if self.images else None,
            videoFrames=[vf.to_dict() for vf in self.video_frames] if self.video_frames else None,
            metadata=self.metadata
        )
