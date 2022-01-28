# author: Adrianne Leung
# date: Jan 2022

def CleverStopwords(words):
    """
    A comprehensive list of English stopwords that allow adding more customized words.    
    
    Parameters
    ----------
    words : set of strings 
        Input a set of words that need to be included in the stopwords 
    
    Returns
    -------
    set of strings  
        The complete set of stopwords 
    
    Examples
    --------
    >>> sample_words = {'disney', 'paris'}
    >>> CleverStopwords(sample_words)
​
    """
    import nltk
    from nltk.corpus import stopwords
    
    # Download stopwords from NLTK library
    nltk.download('stopwords')
    
    # Test input variable type
    if not isinstance(words, set):
        raise TypeError("Input variable should be a set.")

    # Test data type of values of input variable
    for item in words:
        if not isinstance(item, str):
            raise TypeError("Each element of the input should be a string.")

    # NLTK English stopwords
    stopwords = set(stopwords.words("english"))

    try:
        nltk.download("stopwords")
    except:
        raise ImportError("Stopwords are not downloaded from NLTK.")

    new_stopwords = words
    
    # Check for unique new stopwords
    for w in new_stopwords:
        if w is not stopwords:
            # Add customised new words to the existing NLTK stopwords
            stopwords_all = stopwords.union(stopwords, new_stopwords)

    return stopwords_all
