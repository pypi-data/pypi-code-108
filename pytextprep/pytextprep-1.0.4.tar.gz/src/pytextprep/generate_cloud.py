import matplotlib.pyplot as plt
from pytextprep.extract_hashtags import extract_hashtags
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

def generate_cloud(tweets, type="words"):
    """Creates a word cloud of the most frequently occurring
    words in a group of tweets
    
    Parameters
    ----------
    tweets : list
        List of tweets.
    type : {"words", "hashtag", "stopwords"}, default="words"
        Type of content to show in wordcloud. "words" shows all words,
        "hashtag" only shows hashtags, and "stopwords" does not show
        common English words.

    Returns
    -------
    matplotlib.figure.Figure
        Word cloud of most frequently occurring words

    Examples
    --------
    >>> from pytextprep.generate_cloud import generate_cloud
    >>> import matplotlib.pyplot as plt
    >>> tweets = [
        "Make America Great Again! @DonaldTrump #America",
        "It's rocket-science tier investment~~ #LoveElonMusk",
        "America America America #USA #USA"
    ]
    >>> fig, wc = generate_cloud(tweets)
    >>> plt.show()
    """

    nltk.download("stopwords")

    # Check input argument tweets
    if not isinstance(tweets, list):
        raise TypeError("Argument tweets should be of type list.")

    # Check length of argument tweets
    if len(tweets) < 1:
        raise ValueError("Make sure argument tweets contains at least one message")

    # Check that argument tweets only contains strings
    if not all(isinstance(_, str) for _ in tweets):
        raise ValueError("Make sure argument tweets only contains strings")

    # Check input argument type
    if type not in {"words", "hashtag", "stopwords"}:
        raise ValueError("Make sure the argument type is one of the accepted values")

    if type == "words":
        text = (" ".join(tweets)).lower()
        wordcloud = WordCloud(
            max_words=50, background_color="white", stopwords={}
            ).generate(text)
    elif type == "hashtag":
        tweets = extract_hashtags(tweets)
        text = (" ".join(tweets)).lower()
        wordcloud = WordCloud(
            max_words=50, background_color="white", stopwords={}
            ).generate(text)
    else:
        text = (" ".join(tweets)).lower()
        text = " ".join([_ for _ in text.split() if _ not in stopwords.words("english")])
        wordcloud = WordCloud(
            max_words=50, background_color="white"
            ).generate(text)
    
    # Plot word cloud
    fig = plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    return fig, wordcloud