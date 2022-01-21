
def TryFind(string: str, substrings: list, index: int):
    '''
    Returns -1 if none of the substrings could not be found
    '''

    res_i = -1
    # Loop through supstrings
    for substr in substrings:
        # Store string into temporary editable variable
        raw = string
        # Loop through index
        for _ in range(index+1):
            if raw.find(substr) != -1:
                res_i = raw.find(substr)
            # Replace substring to prevent reading the same substring twice
            raw = raw.replace(substr, "█", 1)

        if raw.find("█") != -1:
            return res_i, substr
    return res_i, substr

def ReplaceMultStr(string: str, substrings: list, new_substring: str):
    '''
    Replace multiple substrings of a string
    '''

    for substr in substrings:
        string = string.replace(substr, new_substring)
    return string

def RemoveBetweenChar(string: str, chars: list, n: int=-1):
    '''
    Remove every substring which is between the chars in the chars list
    n: -1 = remove all
    '''

    # Loop through chars
    for char in chars:
        # If n == remove all
        if n == -1:
            while string.count(char) > 0:
                pos_1 = string.find(char)
                pos_2 = string.find(char, pos_1 + 1)

                if (pos_1 == -1 ) | (pos_2 == -1):
                    return string
                string = string[0:pos_1] + string[pos_2+1:]
        # If n != remove all
        else:
            for _ in range(n):
                pos_1 = string.find(char)
                pos_2 = string.find(char, pos_1 + 1)

                if (pos_1 == -1 ) | (pos_2 == -1):
                    return string
                string = string[0:pos_1] + string[pos_2+1:]
                
    return string

def FindIndexReverse(string: str, char: str, offset: int=0):
    '''
    Get the distance to left
    '''

    i = 0
    res_char = ''
    while res_char != char:
        i += 1
        res_char = string[offset-i]
    return offset - i
