from rest_framework.fields import Field


class MediaSerializedField(Field):
    """A custom serializer used to serialize media in Wagtails v2 API."""

    def to_representation(self, val):
        """Return the media URL, title and dimensions."""
        media = []
        for value in val.all():
            media.append(
                {
                    "id": value.featured_media.id,
                    "url": value.featured_media.file.url,
                    "title": value.featured_media.title,
                    "type": value.featured_media.type,
                    "duration": value.featured_media.duration,
                    "width": value.featured_media.width,
                    "height": value.featured_media.height,
                    "thumbnail": value.featured_media.thumbnail.url
                    if value.featured_media.thumbnail
                    else "",
                }
            )

        return media
