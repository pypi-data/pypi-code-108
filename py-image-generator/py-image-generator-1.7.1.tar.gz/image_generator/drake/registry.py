DRAKE_IMAGES = {}
DIRECTORY = '/'.join(__file__.replace('\\', '/').split('/')[:-1] + [''])

def registerDrake(name, imagePath, topCorner, bottomCorner, topWidth, topHeight, bottomWidth, bottomHeight):
    """
    Registers a new image for create a Drake meme.

    :param name:         Name to be used to load the template.
    :param imagePath:    Path to the template image.
    :param topCorner:    Coordinates of the top left corner of the top text area.
    :param bottomCorner: Coordinates of the top left corner of the bottom text area.
    :param topWidth:     Width of the top text area.
    :param topHeight:    Height of the top text area.
    :param bottomWidth:  Width of the top text area.
    :param bottomHeight: Height of the top text area.
    """
    name = name.lower()
    if name not in DRAKE_IMAGES:
        DRAKE_IMAGES[name] = {
            'image': imagePath,
            'top text corner': topCorner,
            # 'top text anchor': (topCorner[0], topCorner[1] + (topHeight / 2)),
            'bottom text corner': bottomCorner,
            # 'bottom text anchor': (bottomCorner[0], bottomCorner[1] + (bottomHeight / 2)),
            'top text width': topWidth,
            'top text height': topHeight,
            'bottom text width': bottomWidth,
            'bottom text height': bottomHeight,
        }

registerDrake('ayano', DIRECTORY + 'drake_ayano_base.png', (242, 2), (242, 247), 240, 235, 240, 235)
registerDrake('chika', DIRECTORY + 'drake_chika_base.png', (258, 2), (258, 260), 244, 250, 244, 250)
registerDrake('drake', DIRECTORY + 'drake_standard_base.png', (243, 2), (243, 246), 242, 239, 242, 239)
registerDrake('sayori', DIRECTORY + 'drake_sayori_base.webp', (487, 2), (487, 473), 471, 458, 471, 490)
registerDrake('sayori_confused', DIRECTORY + 'drake_sayori_confused_base.webp', (378, 3), (378, 365), 366, 352, 366, 353)
