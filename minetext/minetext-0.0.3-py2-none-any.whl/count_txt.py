def count_words_txt(text):
    """
    Count amount of words.
    :param text: input is text data
    :return: Total number of words
    """

    # Define punctuation symbols and numbers.
    punctnum = '''!()-[]{};:'"\,<>./?@#$%^&*_~\n0123456789'''
    textNew = ""

    # Store any elements from text in textNew except for punctuation symbols and numbers.
    for i in text:
        if i not in punctnum:
            textNew = textNew + i

    # Split text into words and count these words.
    lentext = len(textNew.split())
    return lentext


def count_vocab_txt(text):
    """
    Count vocabulary (distinct words) of a text.
    :param text:
    :return:
    """

    # Define punctuation symbols and numbers.
    punctnum = '''!()-[]{};:'"\,<>./?@#$%^&*_~\n0123456789'''
    textNew = ""

    # Store any elements from text in textNew except for punctuation symbols and numbers.
    for i in text:
        if i not in punctnum:
            textNew = textNew + i

    # Split text intp words, convert all words to lowercase, get the distinct words and count them.
    lenvocab = len(set(w.lower() for w in textNew.split()))
    return lenvocab


def count_sents_txt(text):
    """
    ### Count sentences of a text.
    :param text:
    :return:
    """

    # Define punctuation symbols for sentence endings.
    punctuation = '.!?'
    textpuncts = list()

    # Apply conditions if text file is not empty.
    if text != '':

        # Extract sentence ending symbols in text (until text[-2]) and append it to list variable.
        for i in range(len(text) - 1):

            # If sentence ending repeats (like 'What???'), then only extract one sentence ending symbol.
            if text[i] in punctuation and text[i] != text[i + 1]:
                textpuncts.append(text[i])

        # Extract last text element if it is a sentence ending symbol.
        if text[-1] in punctuation:
            textpuncts.append(text[-1])

    # Amount of sentence ending symbols = amount of sentences in the text.
    lensents = len(textpuncts)

    return lensents
