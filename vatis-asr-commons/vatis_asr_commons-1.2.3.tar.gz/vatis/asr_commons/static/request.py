import uuid
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from vatis.asr_commons.domain import Word

from vatis.asr_commons.config.logging import get_logger
from vatis.asr_commons.custom_models import Model

logger = get_logger(__name__)


class TranscriptionResponseFormat(Enum):
    JSON: str = 'JSON'
    PLAIN: str = 'PLAIN'


class TranscriptionRequest:
    def __init__(self, file_uid: str, file_path: Union[str, Path], model: Model, success_url: Optional[str] = None,
                 fail_url: Optional[str] = None, hotwords: Optional[Union[list, str]] = None,
                 hotwords_weight: Optional[float] = None,
                 transcript_format: TranscriptionResponseFormat = TranscriptionResponseFormat.JSON):
        assert file_uid is not None
        assert file_path is not None
        assert model is not None
        assert transcript_format is not None

        self.uid = str(uuid.uuid4())
        self.file_uid: str = file_uid
        self.file_path: str = str(file_path)
        self.model: Model = model
        self.success_url: Optional[str] = success_url
        self.fail_url: Optional[str] = fail_url
        self.hotwords: Optional[List[str]] = None
        self.hotwords_weight: Optional[float] = None
        self.transcript_format: TranscriptionResponseFormat = transcript_format

        if isinstance(hotwords, list):
            self._hotwords = hotwords
        elif isinstance(hotwords, str):
            self._hotwords = list(hotwords.split(','))
        elif hotwords is not None:
            logger.warn(f'Couldn\'t parse hotwords: {hotwords}')

        try:
            if hotwords_weight is not None:
                self._hotwords_weight = float(hotwords_weight)
        except Exception as e:
            logger.exception(f'Couldn\'t parse hotwords weight: {hotwords_weight}. %s', str(e))


class TranscriptionResponse:

    def __init__(self, transcript: List[Word], headers: Dict[str, Any], request: TranscriptionRequest):
        assert transcript is not None
        assert request is not None

        if headers is None:
            headers = {}

        self.transcript: List[Word] = transcript
        self.headers: Dict[str, Any] = headers
        self.request: TranscriptionRequest = request
