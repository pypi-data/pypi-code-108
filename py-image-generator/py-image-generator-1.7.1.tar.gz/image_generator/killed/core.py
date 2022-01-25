from ..utils import singleTextBox


DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])
KILLED_BASE = DIRECTORY + 'killed_base.png'

def createKilled(text, color = (0, 0, 0), font = 'consolas'):
    """
    Creates an "I killed a man" type meme.
    :param text:  The text to insert into the box.
    :param color: A PIL compatible color code for the text color.
    :param font:  A font name that has been loaded into the PTS module.
    """
    return singleTextBox(text, color, font, KILLED_BASE, (29, 396), (258, 73))
