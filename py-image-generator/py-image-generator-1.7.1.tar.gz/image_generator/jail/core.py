import io

import PIL.Image

from ..utils import getPilData


DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])
JAIL_BASE = DIRECTORY + 'jail_base.png'

def createJail(imageData):
    """
    Creates a jail image. :param imageData: should be the raw data stream of an
    image.
    """
    with PIL.Image.open(JAIL_BASE) as base:
        userImage = PIL.Image.open(io.BytesIO(imageData)).resize((1024, 1024), resample = 3)
        userImage.paste(base, (0, 0), mask = base)

        return getPilData(userImage)
