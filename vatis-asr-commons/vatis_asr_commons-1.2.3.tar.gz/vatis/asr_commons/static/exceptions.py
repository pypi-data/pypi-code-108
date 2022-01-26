from vatis.asr_commons.static.request import TranscriptionRequest


class TranscriptionException(Exception):
    def __init__(self, request: TranscriptionRequest, message: str):
        super().__init__(request, message)
        self.request = request
        self.message = message

    def __str__(self):
        return f'Transcription exception: uid={self.request.file_uid}, message={self.message}'

    def __repr__(self):
        return self.__str__()
