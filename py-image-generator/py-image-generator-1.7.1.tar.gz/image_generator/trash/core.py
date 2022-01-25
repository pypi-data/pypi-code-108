import io

import PIL.Image

from ..utils import getPilData


DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])

def rotateFace(imagedata):
    return PIL.Image.open(io.BytesIO(imagedata)).convert('RGBA').rotate(5, resample = 3, expand = True).resize((190, 190), resample = 3)

def generateHand(imagedata):
    im = PIL.Image.open(io.BytesIO(imagedata)).resize((174, 174), resample = 3)
    # for coord in OVERRIDE: # OVERRIDE stores a dictionary of pixel locations to the colors to place at that location.
    #     im.putpixel(coord, OVERRIDE[coord])
    # for coord in TRANSPARENT_COORDS_RELATIVE:
    #     original_color = im.getpixel(coord)
    #     r = TRANSPARENCY_CONVERSIONS[coord]['r'][original_color[0]]
    #     g = TRANSPARENCY_CONVERSIONS[coord]['g'][original_color[1]]
    #     b = TRANSPARENCY_CONVERSIONS[coord]['b'][original_color[2]]
    #     im.putpixel(coord, (r, g, b))
    hand_overlay = PIL.Image.open(DIRECTORY + 'hand_overlay.png')
    im.paste(hand_overlay, mask = hand_overlay)
    return im

def createTrash(face, hand):
    """
    Creates a new trash image.
    """
    faceImage = rotateFace(face)
    handImage = generateHand(hand)
    im = PIL.Image.open(DIRECTORY + 'trash_base.png')
    trashBase = im.convert('RGBA')
    im.close()
    trashBase.paste(handImage, (105, 190))
    trashBase.alpha_composite(faceImage, dest = (375, 80))
    data = getPilData(trashBase)
    trashBase.close()
    return data
