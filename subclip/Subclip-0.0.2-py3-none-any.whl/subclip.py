from collections import Counter

def pair(string, n):
    """
    string: The full text
    n: the number of grams 
    """
    string = string.split()
    ngrams = []
    for i in range(len(string) - n + 1):
        ngrams.append(string[i:i+n])
    return ngrams


def predict(string, phrase, n=0, case_insensitive=False):
    """
    Predicts the next n words of a phrase, given a string.
    string: The full text
    phrase: The phrase that's taken into account
    n: the number of words it should return (Prediction)
    """
    if case_insensitive:
        string = string.lower()
        phrase = phrase.lower()
    string = string.split()
    phrase = phrase.split()
    string, phrase= "<s>".join(string), "<s>".join(phrase)
    string = string.split(phrase)
    string.pop(0)

    string=[" ".join(x.split()[:n]) for x in [x.replace("<s>", " ").lstrip().rstrip() for x in string]]

    return {k: v for k, v in sorted(dict(Counter(string)).items(), reverse=True, key=lambda item: item[1])}


def matchingwords(string_1, string_2):
    """
    Returns a list of words that are present in both strings along with their corresponding frequencies
    """
    string= dict(Counter((string_1 + " " + string_2).split()))
    hashtable = {key:val-1 for key, val in string.items() if val > 1}
    return {k: v for k, v in sorted(hashtable.items(), reverse=True, key=lambda item: item[1])}

def countwords(string, case_insensitive=False):
    """
    Counts the frequency of words in a string
    """
    if case_insensitive:
        string = string.lower()
    return {k: v for k, v in sorted(dict(Counter(string.split())).items(), reverse=True, key=lambda item: item[1])}


def show_vowels_consonants_matrix(string):
    alphabet = [char for char in "abcdefghijklmnopqrstuvwxyz"]
    vowels = ['a', 'e', 'i', 'o', 'u']
    consonants = [char for char in "bcdfghjklmnpqrstvwxyz"]
    matrix = []
    for i in string:
        alphabetindex = alphabet.index(i)
        if i in vowels:
            matrix.append((0, alphabetindex))
        elif i in consonants:
            matrix.append((1, alphabetindex))
    return (string, matrix)


def reconstruct(matrix):
    alphabet = [char for char in "abcdefghijklmnopqrstuvwxyz"]
    string = ""
    for i in matrix:
        string += alphabet[i[1]]
    return string


def syllable_identifier(matrixdata):
    name = matrixdata[0].lower()
    matrix = matrixdata[1]
    #make a list named "word" that stores the first elements of tuples in the matrix
    word = [x[0] for x in matrix]
    final = []
    final.append([])
    for num in range(len(word)):
        i = matrix[num]
        c = i[0]
        if c == 0:
            final[-1].append(i)
        elif c == 1 and len(final[-1]) == 0:
            final[-1].append(i)
        elif c == 1 and final[-1][-1][0] == 0:
            final[-1].append(i)
            final.append([])
        elif c == 1 and final[-1][-1][0] == 1:
            final[-1].append(i)
    for i in range(len(final)-1, -1, -1):
        if len(final[i]) == 0:
            del final[i]
        elif len(final[i]) == 1:
            x = final[i][0]
            del final[i]
            final[-1].append(x)
    final_string = []
    for i in final:
        final_string.append(reconstruct(i))
    return (final, final_string)

#################################
def merge_strings(string1, string2):
    return string1 + string2

def merge_names(splitnames, desired_syllables=None, desired_length=None):
    combinations = []
    for i in splitnames:
        for j in splitnames:
            combinations.append(merge_strings(i, j))

    if desired_length != None:
        combinations = [x for x in combinations if len(x) == desired_length]
    
    if desired_syllables != None:
        combinations = [x for x in combinations if len(syllable_identifier(show_vowels_consonants_matrix(x))[1]) == desired_syllables]
    return combinations
#################################

def syllables(string):
    """
    Splits a word into its syllables. (Case-sensitive)
    """
    return "-".join(syllable_identifier(show_vowels_consonants_matrix(string))[1])
