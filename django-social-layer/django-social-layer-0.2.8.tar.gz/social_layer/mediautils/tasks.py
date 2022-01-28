import os

import logging
from django.conf import settings
from social_layer.mediautils.utils import (cropa_imagem, cropa_video,
                                           convert_towebp,
                                           get_thumb_from_video)

logger = logging.getLogger(__name__)

def formata_all_media(Model=None):
    """ Manipulate media files as needed
    """
    wsize = 480
    hsize = 360
    list_media = Model.objects.filter(formated=False)
    for post in list_media:
        logger.info("processing {} {}...".format(str(Model), str(post.pk)))
        if 'video/' in post.content_type:
            post.formated = cropa_video(post.media_file.path,
                                        larger=wsize, smaller=hsize)
            get_thumb_from_video(post)
            if post.media_thumbnail:
                convert_towebp(post.media_thumbnail.path)
        elif 'image/gif' in post.content_type:
            cropa_imagem(post.media_thumbnail.path, quality=1)
            convert_towebp(post.media_thumbnail.path)
        elif 'image/' in post.content_type:
            if post.media_file:
                cropa_imagem(post.media_file.path, quality=2)
            if post.media_thumbnail:
                cropa_imagem(post.media_thumbnail.path, quality=1)
                convert_towebp(post.media_thumbnail.path)
        post.formated = True
        post.save()
