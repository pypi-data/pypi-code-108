"""
Module containing all the support method of the package.
"""
import io
import json
import pkgutil
import re

import numpy as np
from nltk.stem.snowball import SnowballStemmer
from stop_words import get_stop_words
from textblob import Word

__adjectives_pattern = {
    "it": "[a-zA-Z]*ato",
    "en": "[a-zA-Z]*ed",
}


def __read_json(file_name):
    """
    Get the json file as a dictionary. Json file are stored into the
    provider folder.

    :param file_name: the name of the configuration file.
    :return: a dictionary with the content of json file.
    """
    file = io.BytesIO(pkgutil.get_data(__name__, f"provider/{file_name}"))
    data = json.load(file)
    return data


def __get_categories():
    """
    Get the provided word_to_group file provided into the provider folder.
    This file contains the words for all the supported languages that
    must be simplified if an ingredients contains the word.

    :return: a dict containing the words for each language.
    """
    return __read_json("words_to_group.json")


def __get_excluded_words():
    """
    Get the provided word_to_remove file provided into the provider folder.
    This file contains the words for all the supported languages that
    must be considered as stop words and removed from the recipes.

    :return: a dict containing the words for each language.
    """
    return __read_json("words_to_remove.json")


def __get_stop_words(language="en"):
    """
    Get the stop words of a selected language plus a collection of non-ingredient
    words usually associated with food and ingredients.

    :param language: the language of the stopwords.
    :return: a list containing all the stopwords of the language.
    """
    stop_words = get_stop_words(language)
    return stop_words + __get_excluded_words()[language]


def __strip_numeric(string):
    """
    Remove all the numbers in a string.

    :param string: the string where the numbers must be removed.
    :return: a string without numbers.
    """
    return re.sub(r"\d+", "", string)


def __strip_multiple_whitespaces(string):
    """
    Remove all the multiple spaces in a string.

    :param string: the string where the multiple spaces must be removed.
    :return: a string without multiple spaces.
    """
    return re.sub(" +", " ", string)


def __categorize_words(string, language="en"):
    """
    Categorize a string if it contains one of the words in the
    categories dictionary based on the language. If the string
    doesn't contains any of that words, the string will not be modified.

    :param string: the string that can be categorized.
    :param language: the language of the ingredient and category.
    :return: a categorized string or the same string and a boolean to
    state if the string has been categorized or not.
    """
    category = __get_categories()[language]
    word_list = string.split()
    intersection = list(set(word_list) & set(category))
    return (intersection[0], True) if intersection else (string, False)


def __remove_stopwords(string, language="en"):
    """
    Remove all the stopwords inside the provided string based on
    the provided language.

    :param string: the string where the stopwords must be removed.
    :param language: the language of the ingredient and stopwords.
    :return: a string without stopwords.
    """
    word_list = string.split()
    removed_list = [
        word for word in word_list if word not in __get_stop_words(language)
    ]
    return " ".join(removed_list)


def __remove_punctuation(string):
    """
    Remove all the punctuation symbols and characters in a string.

    :param string: the string where the punctation characters must be removed.
    :return: a string without punctuation.
    """
    return re.sub("[!@#£$.()/-]", "", string)


def __remove_adjectives(string, language="en"):
    """
    Remove all the adjectives in a string: adjectives are words that
    indicate a characteristic of the ingredient.
    (Words like fresh, frozen, ..., end with the same pattern)

    :param string: the string where the adjectives must be removed.
    :param language: the language of the ingredients and adjectives.
    :return: a string without adjectives.
    """
    return re.sub(__adjectives_pattern[language], "", string)


def __stem_word(string, language="en"):
    """
    Produce the stemming of the provided string.
    Stemming is the process of reducing the word to its word stem that
    affixes to suffixes and prefixes or to roots of words known as a lemma.
    Lemmatization only works with english words.

    :param string: the word to be lemmatized.
    :param language: the language of the word.
    :return: the word lemmatized.
    """
    lang = {
        "en": "english",
        "it": "italian",
    }
    stemmer = SnowballStemmer(language=lang[language])
    return stemmer.stem(string)


def process_ingredients(ing, stem=True, language="en"):
    """
    Process all the ingredients string in order to retrieve only the word
    correspond to the single ingredients, without number, special charachters,
    punctuation, stopwords, adjectives and multiple whitespaces.

    :param ing: the string corresponding to the raw ingredient.
    :param language: the language of the ingredient.
    :return: a string corresponding to the single ingredient.
    """
    if not ing:
        return None
    ing = ing.lower()
    ing = ing.replace('"', "")
    ing, boo = __categorize_words(ing, language)
    if not boo:
        ing = __strip_numeric(ing)
        ing = __remove_punctuation(ing)
        ing = __remove_stopwords(ing, language)
        ing = __remove_adjectives(ing, language)
        ing = __strip_multiple_whitespaces(ing)
    ing = __stem_word(ing, language) if stem else ing
    return ing.strip()


def get_embedding(path):
    """
    Get the dataset of ingredients as a dictionary.

    :return: a dictionary representing the embedding
    """
    embedding_io = io.BytesIO(pkgutil.get_data(__name__, path))
    return np.load(embedding_io, allow_pickle=True).item()
