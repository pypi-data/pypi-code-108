from ..utils import topTextBottomText


DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])
REALIZATION_BASE = DIRECTORY + 'realization_base.png'

def createRealization(topText, bottomText, color = (0, 0, 0), topColor = None, bottomColor = None, font = 'consolas', topFont = None, bottomFont = None):
    """
    Create a Realization meme.
    :param topText:     The text to put in the top of the Realization meme.
    :param bottomText:  The text to put in the bottom of the Realization meme.
    :param color:       A PIL compatible color code for the text color.
    :param topColor:    The color to use for the top text. If not specified,
                        this will default to the value of :param color:.
    :param bottomColor: The color to use for the bottom text. If not specified,
                        this will default to the value of :param color:.
    :param font:        A font name that has been loaded into the PTS module.
    :param topFont:     The name of the font to use for the top text.
    :param bottomtFont: The name of the font to use for the bottom text.
    """
    return topTextBottomText(topText, bottomText, color, topColor, bottomColor, font, topFont, bottomFont, REALIZATION_BASE, (2, 2), (467, 242), (2, 250), (467, 242))
