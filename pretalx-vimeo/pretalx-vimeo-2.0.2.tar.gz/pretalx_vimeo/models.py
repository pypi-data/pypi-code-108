from django.db import models


class VimeoLink(models.Model):
    submission = models.OneToOneField(
        to="submission.Submission", on_delete=models.CASCADE, related_name="vimeo_link"
    )
    video_id = models.CharField(max_length=20)

    @property
    def player_link(self):
        return f"https://player.vimeo.com/video/{self.video_id}"

    @property
    def vimeo_link(self):
        return f"https://vimeo.com/video/{self.video_id}"

    @property
    def iframe(self):
        return f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{self.player_link}" frameborder="0" allowfullscreen></iframe></div>'

    def serialize(self):
        return {
            "submission": self.submission.code,
            "vimeo_link": self.vimeo_link,
        }
