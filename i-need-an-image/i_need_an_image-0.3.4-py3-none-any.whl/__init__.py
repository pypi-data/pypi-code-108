import logging
import sys
from need_an_image.engines import ENGINES
from need_an_image.utils.store import save_image

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def need_image_from(engine, keyword, exact=True, allow_pos=(), save_to=None, max_retry=3):
    image = ENGINES[engine].get_an_image(keyword=keyword, exact=exact, allow_pos=allow_pos, max_retry=max_retry)

    if image is None:
        return

    if save_to:
        filename = save_image(image, save_to=save_to)
        return filename

    return image
