import io

import PIL.Image

from ..utils import getPilData


DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])
SHIP_BASE = DIRECTORY + 'ship_base.png'

def createShip(leftImageData, rightImageData):
    """
    Creates a ship image. Each image data should be the raw data stream of an
    image.
    """
    with PIL.Image.open(SHIP_BASE) as base:
        user1Image = PIL.Image.open(io.BytesIO(leftImageData))
        user2Image = PIL.Image.open(io.BytesIO(rightImageData))
        base.paste(user1Image.resize((128, 128), resample = 2), (0, 0))
        base.paste(user2Image.resize((128, 128), resample = 2), (256, 0))
        user1Image.close()
        user2Image.close()

        return getPilData(base)
