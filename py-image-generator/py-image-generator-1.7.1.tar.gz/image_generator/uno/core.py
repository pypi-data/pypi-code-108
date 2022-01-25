import PIL.Image
import PIL.ImageDraw
import PTS

from ..utils import calculatePositionFullCenter, getPilData


DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])
UNO_BASE = DIRECTORY + 'uno_base.jpg'
UNO_NO_NUMBER_BASE = DIRECTORY + 'uno_no_number_base.png'

def createUno(cardText, faceText = '', color = (0, 0, 0), cardColor = None, faceColor = None, font = 'consolas', cardFont = None, faceFont = None, number = 25):
    """
    Creates an UNO meme image.
    :param cardText:  The text to put on the card.
    :param faceText:  The text to put on the face, if any.
    :param color:     The color to use for all text, should a specific section
                      not be specified.
    :param cardColor: The color of the text to put on the card.
    :param faceColor: The color of the test to put on the face.
    :param font:      The font to use for all text, should a specifc section not
                      be specified.
    :param cardFont:  The font to use for the card text.
    :param faceFont:  The font to use for the face text.
    :param number:    The number to be used on the card. If this is anything
                      other than 25 a seperate meme base will be used.
    """
    # Get the colors.
    cardColor = cardColor or color
    faceColor = faceColor or color

    # Get the fonts.
    cardFont = cardFont or font
    faceFont = faceFont or font

    # Process the number
    if number != 25:
        useNumber = True
        base = UNO_NO_NUMBER_BASE
        if not isinstance(number, int):
            raise TypeError(':param number: must be an int.')
        if number > 99999:
            raise ValueError('Number must not be greater than 99999.')
    else:
        useNumber = False
        base = UNO_BASE

    # Get the formtted text.
    cardTextFinal = PTS.fitText(cardText, 145, 84, cardFont, fast = True)
    faceTextFinal = PTS.fitText(faceText, 243, 64, faceFont, fast = True) if faceText else None
    numberTextFinal = PTS.fitText(str(number), 80, 60, 'Comic Sans Bold') if useNumber else None


    cardTextSize = cardTextFinal[1].getsize_multiline(cardTextFinal[0])
    posCard = calculatePositionFullCenter(84, 164, 145, cardTextSize[0], 84, cardTextSize[1])

    if faceText:
        faceTextSize = faceTextFinal[1].getsize_multiline(faceTextFinal[0])
        posFace = calculatePositionFullCenter(254, 2, 243, faceTextSize[0], 64, faceTextSize[1])

    if useNumber:
        numberTextSize = numberTextFinal[1].getsize_multiline(numberTextFinal[0])
        posNumber = calculatePositionFullCenter(40, 330, 80, numberTextSize[0], 60, numberTextSize[1])

    # Load the image and prepare for drawing.
    with PIL.Image.open(base) as im:
        draw = PIL.ImageDraw.ImageDraw(im)

        # Draw the text.
        draw.text(posCard, cardTextFinal[0], cardColor, cardTextFinal[1])
        if faceText:
            draw.text(posFace, faceTextFinal[0], faceColor, faceTextFinal[1], align = 'center')
        if useNumber:
            draw.text(posNumber, numberTextFinal[0], (46, 38, 32), numberTextFinal[1])

        # Save the data and return it as a png image.
        return getPilData(im)
