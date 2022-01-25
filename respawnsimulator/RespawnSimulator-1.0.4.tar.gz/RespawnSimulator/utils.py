Settings = {
    "DEBUG": True,
    "DEBUG_LEVEL": 5
}


def echo(word, color=1):
    print(word)


def debugOut(identity, word, left_color=1, right_color=1, level=2):
    if Settings["DEBUG"] and Settings["DEBUG_LEVEL"] >= level:
        print("[{0}]:{1}".format(identity, word))


def divide(value, sep):
    parts = value.split(sep)
    if len(parts) > 1:
        return parts[0], parts[1]
    else:
        return parts[0], ""
