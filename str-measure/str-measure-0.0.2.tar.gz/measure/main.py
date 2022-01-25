import unicodedata

def get_length(message):
    string_length = 0
    for i in message:
        letter = unicodedata.east_asian_width(i)
        if letter == 'H':
            string_length =+ 1
        elif letter == 'Na':
            string_length =+ 1
        elif letter == 'F':
            string_length =+ 2
        elif letter == 'A':
            string_length =+ 2
        elif letter == 'W':
            string_length =+ 2
        else:
            string_length =+ 1
    return string_length