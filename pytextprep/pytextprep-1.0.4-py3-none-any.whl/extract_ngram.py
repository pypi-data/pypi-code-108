def extract_ngram(tweets, n):
    """Extracts n-grams from the input tweet data
    
    Parameters
    ----------
    tweets : array_like
        List of tweets
    n : int
        Length of n-grams to be created

    Returns
    -------
    list
        List of n-grams generated

    Examples
    --------
    >>> tweets_list =[
        "Make America Great Again DonaldTrump",
    ]  
    >>> extract_ngram(tweets=tweets_list, n=3)
    [
        "Make America Great",
        "America Great Again",
        "Great Again DonaldTrump"
    ]
    """
    # Check for correct input type
    if not isinstance(tweets, list):
        raise TypeError("'tweets' should be of type 'list'.")

    # Convert array like input to string
    s =  " ".join(tweets)
    
    # Break tweets into individual words
    words = [word for word in s.split(" ") if word != ""]

    # Use the zip function to generate n-grams
    ngrams = zip(*[words[i:] for i in range(n)])

    # Concatenate and return ngrams
    return [" ".join(ngram) for ngram in ngrams]
