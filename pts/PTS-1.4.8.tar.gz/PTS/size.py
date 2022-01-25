import threading

FAST_LOCK = threading.Lock()
FAST_FONTS = {}

def createFastFont(fonts):
    """
    Creates a fast version of the specified Font object. While slightly less
    accurate, it is extremly fast.
    """
    for font in fonts:
        if font not in FAST_FONTS:
            try:
                with FAST_LOCK:
                    FAST_FONTS[font] = {chr(x): font.getsize_multiline(chr(x)) for x in range(256)}
            except OSError as e:
                if str(e) == 'unknown freetype error':
                    with FAST_LOCK:
                        FAST_FONTS[font] = {chr(x): font.getsize_multiline(chr(x)) for x in range(256)}
                else:
                    raise

def getSizeFast(text, font):
    """
    Faster version of the function of a Font object used for getting the size of
    a string of text. If a fast version of the Font object does not exist, it
    will automatically use the slow version of the function.
    """
    if font in FAST_FONTS:
        ffont = FAST_FONTS[font]
        lines = tuple(getSizeLine(line, font, ffont) for line in text.split('\n'))
        return (max(line[0] for line in lines), sum(line[1] for line in lines) + (4 * len(lines)))
    else:
        return getSizeSlow(text, font)

def getSizeLine(line, font, fastFont):
    return sumSizes(fastFont[char] if char in fastFont else font.getsize_multiline(char) for char in line)

def getSizeSlow(text, font):
    return font.getsize_multiline(text)

def sumSizes(sizes):
    """
    Takes in an iterable of sizes and returns the sums of each for a line.
    """
    sizes = tuple(sizes)
    return (sum(x[0] for x in sizes), max(x[1] for x in sizes))
