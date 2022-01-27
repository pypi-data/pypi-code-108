import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from string import punctuation
from nltk.tokenize import RegexpTokenizer

# Count number of punctuations
def count_punc(text):
    """
    Count the number of punctuations within the text.
    
    Parameters
    ----------
    text : str
        piece of text to analyze

    Returns
    -------
    integer
        the number of punctuations

    Examples
    --------
    >>> count_punc("Hello, World!")
    2
    >>> count_punc("Hello World")
    0
    """
    if not isinstance(text, str): 
        raise TypeError("'text' should be of type 'String'")
    count = 0
    for ch in text:
        if ch in punctuation:
            count += 1
    return count
    
# Average word length
def avg_word_len(text):
    """
    Calculate the average length of the words within the text.

    Parameters
    ----------
    text : str
        piece of text to analyze

    Returns
    -------
    float
        the average length of words within the text

    Examples
    --------
    >>> avg_word_len("Hello, World!")
    5
    """
    if not isinstance(text, str):
        raise TypeError("'text' should be of type 'String'")
    
    try:
        from string import punctuation
    except ImportError:
        raise ImportError("punctuation from string module failed to import")
    
    new_text = ""
    for char in text:
        if char not in punctuation:
            new_text = new_text + char
        else:
            new_text = new_text + " "
    
    word_len = [len(word) for word in new_text.split()]

    if len(word_len) == 0:
        average_len = 0
    else:
        average_len = sum(word_len) / len(word_len)
    
    return average_len

# Count percentage of fully capitalised words
def perc_cap_words(text):
    """
    Calculate percentage of fully capitalised words in the text.

    Parameters
    ----------
    text : str
        the input text
    
    Returns
    -------
    float
        percentage of capitalised words
    
    Examples
    --------
    >>> perc_cap_words("THIS is a SPAm MESSage.")
    20
    >>> perc_cap_words("THIS is a SPAM MESSAGE.")
    60
    """
    if text == " " or text == "":
        raise TypeError("'text' should not be empty!")
    if not isinstance(text, str):
        raise TypeError("'text' should be of type 'String'")

    tokenizer = RegexpTokenizer(r'\w+')                # Tokenizer created to select word character and ignores punctuations and numbers
    count_cap_words = 0                                # Initialises the count for the number of capitalised words
    words = text.split(' ')                            # Splits the string based on spaces
    for word in words:
        if word.isupper():
            count_cap_words += 1                       # Adds one to the count if the entire word is uppercase
    
    return (count_cap_words / len(tokenizer.tokenize(text)) * 100)

# Remove stopwords
def remove_stop_words(text, language="english"):
    """
    Remove stop words from the text and return the list of clear words in the text.

    Parameters
    ----------
    text : str
        piece of text to analyze
    language : str (optional)
        the language of the text (default = 'english')

    Returns
    -------
    list
        the list of the words in the text that are not stop words.

    Examples
    --------
    >>> remove_stop_words("Tomorrow is a big day!")
    ['tomorrow', 'big', 'day!']
    """
    if text == " " or text == "":
        raise TypeError("'text' should not be empty!")
    
    if language not in stopwords.fileids():
        raise TypeError("Please provide a valid language!")
    
    if not isinstance(text, str):
        raise TypeError("'text' should be of type 'String'")
    
    stop_words = set(stopwords.words(language))   # Create set of stop words to increase the efficiency of searching elements
    words = text.lower().split(" ")               # Create list of the words in the text
    clean_words = []                              # Create an empty list to store the words that are not in the stop words

    for word in words:
        if word not in stop_words:
            clean_words.append(word)
    
    return clean_words
  