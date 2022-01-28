import os
from django.db import models
from django.utils import timezone

# Create your models here.
def _choose_upload_media_to(instance, filename, dir_prefix):
    """ choose directory to upload files
    """
    if len(filename) > 5:
        filepath = "{}/{}/{}".format(filename[:2], filename[:4], filename)
    else:
        filepath = filename
    name = dir_prefix + filepath
    return name


def choose_upload_media_to(instance, filename):
    """ where to upload the main file """
    return _choose_upload_media_to(instance, filename, 'files/sl/')


def choose_upload_media_thumb_to(instance, filename):
    """ where to upload the thumbnail file """
    return _choose_upload_media_to(instance, filename, 'files/sl/thumbs/')


class Media(models.Model):
    """ abstract class for media objects """
    media_file = models.FileField(upload_to=choose_upload_media_to,
                                                    max_length=10485760)
    media_thumbnail = models.FileField(upload_to=choose_upload_media_thumb_to,
                                                    max_length=10485760,
                                                    null=True, blank=True)
    content_type = models.CharField(max_length=127, null=True, blank=True,
                                    default='application/octet-stream')
    orientation = models.CharField(max_length=10, default='portrait')

    format_tries = models.IntegerField(default=0)
    formated = models.BooleanField(default=False)
    md5_hash = models.CharField(max_length=32, null=True, blank=True)

    class Meta():
        abstract = True

    def save(self, *args, **kwargs):
        from social_layer.mediautils.utils import get_img_orientation
        super(Media, self).save(*args, **kwargs)
        # Try to guess image orientation
        if 'image/' in self.content_type:
            self.orientation = get_img_orientation(self.media_file.path)
        elif self.media_thumbnail:
            self.orientation = get_img_orientation(self.media_thumbnail.path)
        super(Media, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        attr_list = [ 'media_file', 'media_thumbnail' ]
        for attr in attr_list:
            arquivo = getattr(self, attr, None)
            if (arquivo and os.path.isfile(arquivo.path)):
                os.remove(arquivo.path)
        super(Media, self).delete(*args, **kwargs)
