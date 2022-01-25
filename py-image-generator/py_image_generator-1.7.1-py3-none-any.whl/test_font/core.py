import PIL.Image
import PIL.ImageDraw
import PTS

from ..utils import calculatePositionFullCenter, getPilData


def createFontTest(font, text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-_=+,.<>/?\\|\'"[]{}`~'):
    """
    Returns an image containing the specified text in the specified font.
    """
    # Get the size data for the font.
    fontData = PTS.getSize(font)

    # Get the largest font instance.
    font = PTS.core.FONTS[font.lower()][max(range(fontData['min'], fontData['max'], int(abs(fontData['step']))))]

    # Calculate how big an image would need to be to fit the specified text.
    size = font.getsize(text)

    # Create the size tuple for the new image.
    imageSize = (int(size[0] * 1.1), int(size[1] * 5))
    if imageSize[0] - size[0] < 10:
        imageSize = (imageSize[0] + 10, imageSize[1])

    # Get the position to place the text.
    drawPosition = calculatePositionFullCenter(0, 0, imageSize[0], size[0], imageSize[1], size[1])

    # Create the image.
    with PIL.Image.new('RGB', imageSize, (255, 255, 255)) as im:
        draw = PIL.ImageDraw.ImageDraw(im)

        # Draw the text.
        draw.text(drawPosition, text, (0, 0, 0), font)

        # Get the image data and return it.
        return getPilData(im)
