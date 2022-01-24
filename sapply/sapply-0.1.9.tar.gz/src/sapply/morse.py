MORSE = {
    'A': '.-'        , 'B': '-...'    , 'C': '-.-.'    ,
    'D': '-..'       , 'E': '.'       , 'F': '..-.'    ,
    'G': '--.'       , 'H': '....'    , 'I': '..'      ,
    'J': '.---'      , 'K': '-.-'     , 'L': '.-..'    ,
    'M': '--'        , 'N': '-.'      , 'O': '---'     ,
    'P': '.--.'      , 'Q': '--.-'    , 'R': '.-.'     ,
    'S': '...'       , 'T': '-'       , 'U': '..-'     ,
    'V': '...-'      , 'W': '.--'     , 'X': '-..-'    ,
    'Y': '-.--'      , 'Z': '--..'    , '1': '.----'   ,
    '2': '..---'     , '3': '...--'   , '4': '....-'   ,
    '5': '.....'     , '6': '-....'   , '7': '--...'   ,
    '8': '---..'     , '9': '----.'   , '0': '-----'   ,
    ', ' :'--..--'   , '.': '.-.-.-'  , '?': '..--..'  ,
    '/': '-..-.'     , '-': '-....-'  , '(': '-.--.'   ,
    ')': '-.--.-'
}

def to_morse(msg):
    output = ''
    for char in msg:
        if char != ' ':
            output += MORSE[char] + ' '
        else:
            # 1 space indicates different characters
            # and 2 indicates different words
            output += ' '
    return output

def to_ascii(msg):
    # extra space added at the end to access the
    # last morse code
    msg += ' '
    output = ''
    morse = ''
    for char in msg:
        if (char != ' '):
            i = 0 # keep track of space
            morse += char
        else:
            i += 1              # i == 1 indicates a new character
            if i == 2 :         # i == 2 indicates a new word
                output += ' '   # adding space to separate words
            else:
                # convert morse to ascii
                output += list(MORSE.keys())[list(MORSE.values()).index(morse)]
                morse = ''
    return output
