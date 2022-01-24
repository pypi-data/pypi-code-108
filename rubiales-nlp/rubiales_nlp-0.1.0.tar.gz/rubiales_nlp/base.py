'''
Author: Alberto Rubiales Borrego
Mail: al.rubiales.b@gmail.com
Github: arubiales
Created Date: 24-Jan-2022
-----
Last Modified: 24-Jan-2022
Modified By: Alberto Rubiales Borrego
-----
'''
from itertools import chain
from collections import Counter
from typing import List, Dict, Set
import re
import nltk


def word_counter(corpus: List[str]) -> Dict[str, int]:
    """
    Count all the times a word appear in a corpus

    Arguments:
    corpus: List[str]
        The corpus with all sentences

    Returns
    ---------
    Dict[str, int]: The corpus's wordcount
    """
    corpus = list(chain(*corpus))
    count = Counter(corpus)
    count = dict(sorted(count.items(), key=lambda dictionary: dictionary[1], reverse=True))
    return count


def sentence_length(corpus: List[str]) -> List[int]:
    """
    Compute the length of each sentence in the corpush

    Arguments
    ----------
    corpus: List[str]
        A list of sentences

    Returns
    --------
    List[int]: the length of each sentence
    """
    sentences_length = []
    for sentence in corpus:
        sentences_length.append(len(sentence))
    return sentences_length


# This function is used when FeatureEnginieringNLP is very compuntationally expensive
def clean_and_tokenize(string: str) -> str:
    """
    Clean points, do lower and tokenize the whole corpus
    Arguments
    ----------
    string: str
        A sentence of the corpus
    Returns
    --------
    A string that is the sentence without points, lowered and tokenized
    """
    string = re.sub("[.,:;]", "", string)
    string = string.lower()
    return nltk.tokenize.treebank.TreebankWordTokenizer().tokenize(string)


class RemoveStopWords:
    """
    Class to add and stopwords

    Arguments
    ----------
    language: str
        The language of the stopwords

    Methods
    --------

    add_stopwords: A set of stopwords to add
    fit: The string to clean the stopwords
    """

    def __init__(self, language: str = "english") -> None:
        self.stopwords = set(nltk.corpus.stopwords.words(language))

    def fit(self, string: List[str]) -> List[str]:
        """
        Clean the stopwords from a tokenized sentence

        Arguments
        -----------
        string: str
            The sentence to clean the stopwords

        Returns:
            The sentence cleaned
        """
        return [word for word in string if word not in self.stopwords]

    def add_stopwords(self, stopwords: Set[str]) -> None:
        """
        Add a set of stopwords to clean

        Arguments:
        -----------
        stopwords: set[str]
            A set of words to add in order to be cleaned from the sentence
        """
        self.stopwords = self.stopwords | set(stopwords)
