class FontError(KeyError):
    font = None
    def __init__(self, font):
        KeyError.__init__(self, 'Could not find the font "{}" (did you load it and use the right name?).'.format(font))
        self.font = font
