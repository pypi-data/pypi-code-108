import PIL.Image
import PIL.ImageDraw
import PTS

from ..utils import calculatePositionAlign, getPilData
from ..enums import Alignment


def createTextImage(text : str, font : str, imageSize = (1920, 1080), textColor = (255, 255, 255), bgColor = (0, 0, 0), alignment : Alignment = Alignment.CENTER_CENTER):
    """
    Creates an image with text in it, aligned by default to the center. Will not
    automatically wrap the text.

    :param text:      The text to write.
    :param font:      The font to use for the text. Must be an actual font
                      object.
    :param imageSize: A tuple of the image size.
    :param textColor: The color of the text. Defaults to white.
    :param bgColor:   The color of the background. Defaults to black.
    :param alignment: The method to use for aligning the text. Must be an
                      instance of the Alignment enum or convertable. Defaults to
                      center.
    """
    # Check to make sure we have usable text.
    if not text:
        raise ValueError('You must specify text to place in the image.')

    # Make sure he have an alignment object and convert it to one otherwise.
    alignment = Alignment.convert(alignment)

    # Create the new image.
    with PIL.Image.new('RGB', imageSize, bgColor) as im:
        # Create the ImageDraw.
        draw = PIL.ImageDraw.ImageDraw(im)
        # Get the size of our text.
        size = draw.multiline_textsize(text, font)
        # Make sure the text won't overflow.
        if size[0] > imageSize[0] or size[1] > imageSize[1]:
            raise ValueError('The text is too big to fit in this image size.')
        position = calculatePositionAlign((0, 0), imageSize, size, alignment)

        draw.multiline_text(position, text, fill = textColor, font = font)

        return getPilData(im)
