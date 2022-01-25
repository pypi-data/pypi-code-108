import PIL.Image
import PIL.ImageDraw
import PTS

from .registry import DRAKE_IMAGES
from ..exceptions import TemplateError
from ..utils import calculatePositionVerticalCenter, getPilData


def createDrake(template = 'drake', topText = '', bottomText = '', color = (0, 0, 0), topColor = None, bottomColor = None, font = 'consolas', topFont = None, bottomFont = None):
    """
    Create a Drake meme.
    :param template:    The name of the template to use.
    :param topText:     The text to put in the top of the Drake meme.
    :param bottomText:  The text to put in the bottom of the Drake meme.
    :param color:       A PIL compatible color code for the text color.
    :param topColor:    The color to use for the top text. If not specified,
                        this will default to the value of :param color:.
    :param bottomColor: The color to use for the bottom text. If not specified,
                        this will default to the value of :param color:.
    :param font:        A font name that has been loaded into the PTS module.
    :param topFont:     The name of the font to use for the top text.
    :param bottomtFont: The name of the font to use for the bottom text.
    """
    # Check that top text and bottom text are not empty
    if not topText:
        raise ValueError(':param topText: must not be empty.')
    if not bottomText:
        raise ValueError(':param bottomText: must not be empty.')

    # Load the template.
    template = DRAKE_IMAGES.get(template.lower())
    if not template:
        raise TemplateError(template)

    # Set the colors.
    topColor = topColor or color
    bottomColor = bottomColor or color

    # Set the fonts.
    topFont = topFont or font
    bottomFont = bottomFont or font

    # Prepare the text.
    topTextFinal = PTS.fitText(topText, template['top text width'], template['top text height'], topFont, fast = True)
    if topTextFinal is None:
        raise OverflowError('Top text is too long to fit in the specified space.')

    bottomTextFinal = PTS.fitText(bottomText, template['bottom text width'], template['bottom text height'], bottomFont, fast = True)
    if bottomTextFinal is None:
        raise OverflowError('Top text is too long to fit in the specified space.')

    # Determine exactly where to put the text.
    posTop = calculatePositionVerticalCenter(template['top text corner'][0], template['top text corner'][1], template['top text height'], topTextFinal[1].getsize_multiline(topTextFinal[0])[1])
    posBottom = calculatePositionVerticalCenter(template['bottom text corner'][0], template['bottom text corner'][1], template['bottom text height'], bottomTextFinal[1].getsize_multiline(bottomTextFinal[0])[1])

    # Load the template image.
    with PIL.Image.open(template['image']) as im:
        draw = PIL.ImageDraw.ImageDraw(im)

        # Place the text in the image.
        draw.text(posTop, topTextFinal[0], topColor, topTextFinal[1])
        draw.text(posBottom, bottomTextFinal[0], bottomColor, bottomTextFinal[1])

        # Save the data and return it as a png image.
        return getPilData(im)
