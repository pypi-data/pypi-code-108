import re

def extract_hashtags(tweets):
    """Extracts all hashtags included in the input tweet data
    
    Parameters
    ----------
    tweets : array_like
        List of tweets

    Returns
    -------
    list
        List of hashtags included in the tweets list

    Examples
    --------
    >>> tweets_list = [
        "Make America Great Again! @DonaldTrump",
        "It's rocket-science tier investment~~ #LoveElonMusk"
    ]
    >>> extract_hashtags(tweets_list)
    [
        "LoveElonMusk"
    ]
    """
    # Check for correct input type
    if not isinstance(tweets, list):
        raise TypeError("'tweets' should be of type 'list'.")

    # Convert array like input to string
    text =  " ".join(tweets)
    
    # Break tweets into individual words
    htags = re.findall(r'(#[A-Za-z0-9]*)', text)
    htags = [ht.replace('#', '') for ht in htags]
    return htags