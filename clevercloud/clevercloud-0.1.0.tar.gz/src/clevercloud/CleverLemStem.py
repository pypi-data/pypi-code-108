def CleverLemStem(text):
    """
    A preprocessor to conduct lemmatinzation and stemming on the text.   
    
    Parameters
    ----------
    text : str
        Input a string
    
    Returns
    -------
    str
        The lemmatized and stemmed string 
    
    Examples
    --------
    >>> sample_text = "maximum crying feet"
    >>> CleverLemStem(sample_text)
    "maxim cry foot"
    """
    # check the type of the imput 
    if not isinstance(text, str):
        raise TypeError("The input value should be a string.")
    
    # import packages 
    import nltk
    from nltk.stem import LancasterStemmer, WordNetLemmatizer
    from nltk.tokenize import RegexpTokenizer
    nltk.download('omw-1.4')
    nltk.download('wordnet')
    
    # lemmatization 
    tokenizer = RegexpTokenizer(r'\w+')
    tokenized_text = tokenizer.tokenize(text)
    lem = WordNetLemmatizer()
    lem_text = ' '.join([lem.lemmatize(i) for i in tokenized_text])
    
    # stemming 
    tokenized_lem_text = tokenizer.tokenize(lem_text)
    stemmer = LancasterStemmer()
    clean_text = ' '.join([stemmer.stem(i) for i in tokenized_lem_text]) 
    
    return clean_text
