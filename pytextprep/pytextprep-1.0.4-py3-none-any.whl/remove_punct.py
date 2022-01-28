import re
import numpy as np

def remove_punct(tweets, skip=None):
    """Remove all punctuation and special characters from the
    input tweets data

    Parameters
    ----------
    tweets : array_like
        List of tweets 

    skip : array_like or None, optional
        The set of characters that do not have to be removed.
        Default is None. If None, all characters except alphabets,
        numbers and space would be removed.

    Returns
    -------
    list
        list of tweets without special characters

    Examples
    --------
    >>> tweets_list = [
        "Make America Great Again! @DonaldTrump",
        "It's rocket-science tier investment~~ #LoveElonMusk"
    ]

    >>> remove_punct(tweets_list)
    [
        "Make America Great Again DonaldTrump",
        "Its rocketscience tier investment LoveElonMusk"
    ]   

    >>> remove_punct(tweets_list, skip=["'", "@", "#", '-'])
    [
        "Make America Great Again @DonaldTrump",
        "It's rocket-science tier investment #LoveElonMusk"
    ]

    """
    if not hasattr(tweets, "__len__") or isinstance(tweets, str):
        raise TypeError("Tweets must be array_like Object")
    orig_shape = None
    if isinstance(tweets, np.ndarray) and (len(tweets.shape) > 1):
        orig_shape = tweets.shape
        tweets = tweets.flatten()
    out_tweets = tweets.copy()
    for i, t in enumerate(tweets):
        if skip is None:
            punct_regex = f"[^A-Za-z\s\d]"
        else:        
            punct_regex = f"[^A-Za-z\s\d{''.join(skip)}]"
        t_no_punct = re.sub(punct_regex, "", t)
        out_tweets[i] = t_no_punct
    if orig_shape is not None:
        out_tweets = out_tweets.reshape(*orig_shape)
    return out_tweets