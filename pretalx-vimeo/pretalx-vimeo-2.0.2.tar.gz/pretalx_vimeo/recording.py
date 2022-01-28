from pretalx.agenda.recording import BaseRecordingProvider


class VimeoProvider(BaseRecordingProvider):
    def get_recording(self, submission):
        vimeo = getattr(submission, "vimeo_link", None)
        if vimeo:
            return {"iframe": vimeo.iframe, "csp_header": "https://player.vimeo.com"}
