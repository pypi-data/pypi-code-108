
# Script that can clean the text in a dataframe

from pandas.core.frame import DataFrame
import preprocessor as pp
import pandas as pd
import emoji
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('wordnet')


df = pd.DataFrame(["one", 'towoi', ';ldkfjs;ijf;e', 'djf;sldkfj;sodikj'])
df = df[df[0].str.len() < 10]
df.head()

# The stopwords that were used come from here (go to the google stop word section):
# https://www.ranks.nl/stopwords
stop_words = ["i","a","about","an","are","as","at","be","by","com","for","from","how","in","is","it","of","on","or","that","the","this","to","was","what","when","where","who","will","with","the","www"]

def clean_text(df, text_column, bert_cleaning=False, tweet_length=240):
    """Cleans the text column in a pandas dataframe. Drops rows wich have empty fields in the text column and duplicates in the text column"""

    # Remove "tweets" that are longer than 280 characters
    df = df[df[text_column].str.len() < 280]

    # Changes all url's and mentions to a token that's the same for all urls and a token that's the same for all mentions
    # This: 
    # Preprocessor is #awesome 👍 https://github.com/s/preprocessor @test
    # Becomes this:
    # 'Preprocessor is #awesome 👍 $URL$ $MENTION$'
    # Go here for the documentation on pp: https://pypi.org/project/tweet-preprocessor/ 
    pp.set_options(pp.OPT.URL, pp.OPT.MENTION)
    df[text_column] = [pp.tokenize(text) for text in df[text_column]]

    # Removing punctuation
    # This: Won't !#$% *&^ hallo?, does this work?
    # becomes this: Wont hallo does this work
    df[text_column] = [re.sub("[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", '', text) for text in df[text_column]] 

    # Change emoji's into tokens too but give every emoji it's own token
    # 'Python is 👍' Becomes: 'Python is :thumbs_up:'
    # The documentation for the emoji module is here: https://pypi.org/project/emoji/ 
    df[text_column] = [emoji.demojize(text) for text in df[text_column]]
    df[text_column] = [re.sub(":", '', text) for text in df[text_column]] 

    # Changing every upper case letter to lower case
    df[text_column] = df[text_column].str.lower()

    # Removing unneeded white spaces from the text
    df[text_column] = [re.sub('\s+', ' ', text) for text in df[text_column]]

    # If we're cleaning the data for a bert model we might want to leave in stop words and unlemmatized versions of words
    # because context is important for bert.
    if not bert_cleaning:
        # Lemmatizing the text

        # For lemmatizing we need to know what type of word a word is to lemmatize it.
        # The pos_tag function that is used to figure out what the word types are uses 
        # strings to say what the word types are, but the algorithm that does the 
        # lemmatization needs a different variable type so this function translates 
        # between the two. (pos stands for part of speech, which is the same thing as word type)
        def get_wordnet_pos(treebank_tag):
            if treebank_tag.startswith('J'):
                return wordnet.ADJ
            elif treebank_tag.startswith('V'):
                return wordnet.VERB
            elif treebank_tag.startswith('N'):
                return wordnet.NOUN
            elif treebank_tag.startswith('R'):
                return wordnet.ADV
            else:
                return wordnet.NOUN
        
        # The object that is going to lemmatize the words
        lemmatizer = WordNetLemmatizer()

        def lemmatize_sentence(text):
            # Tagging the words with their type of word
            tagged_words = nltk.pos_tag(nltk.word_tokenize(text))
            # lemmatizing the words
            lemmatized_sentence = [
                lemmatizer.lemmatize(word[0], get_wordnet_pos(word[1])) for word in tagged_words
            ]
            return ' '.join(lemmatized_sentence)

        df[text_column] = [lemmatize_sentence(text) for text in df[text_column]]

        # removing stop words
        def remove_stop_words(text):
            tokenized_sentence = nltk.word_tokenize(text)
            tokenized_sentence = ["" if token in stop_words else token for token in tokenized_sentence]
            return ' '.join(tokenized_sentence)
        df[text_column] = [remove_stop_words(text) for text in df[text_column]]

    # dropping emty rows and duplicate rows (only looking at the text column)
    df = df.dropna(subset=[text_column]).drop_duplicates(subset=[text_column])
    df = df[df[text_column].str.len() < 280]

    return df