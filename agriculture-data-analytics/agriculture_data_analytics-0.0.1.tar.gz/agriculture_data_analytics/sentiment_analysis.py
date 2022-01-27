from pandas import DataFrame
from textblob import TextBlob
import spacy

nlp = spacy.load('en_core_web_sm')


def clear_html_characters(html_text: str) -> str:
    value_pairs: dict = {
        '(<br/>)': '',
        '(<a).*(>).*(</a>)': '',
        '(&amp)': '',
        '(&gt)': '',
        '(&lt)': '',
        '(\xa0)': ' ',
    }
    for key, value in value_pairs.items():
        html_text = html_text.replace(key, value, regex=True)

    return html_text


dependency_to_delete = ['NUM', 'INTJ', 'CONJ', 'ADV',
                        'PUNCT', 'PART', 'DET', 'ADP', 'SPACE', 'PRON', 'SYM', 'x']


def spacy_clean(text: str) -> str:
    spacy_text = ""
    doc = nlp(text)
    for token in doc:
        if token.is_stop == False and token.is_alpha and len(token) > 2 and token.pos_ not in dependency_to_delete:
            spacy_text += token.lemma_ + " "
    return spacy_text.rstrip()


def add_clean_text_columns(dataframe, text_column="text") -> DataFrame:
    """
    This function takes a dataframe and adds a column with a cleaned version of the text.
    :param dataframe: DataFrame
    :param text_column: str
    :return: DataFrame
    """
    dataframe["clean_text"] = clear_html_characters(
        dataframe[text_column].str.lower())
    dataframe['clean_text'] = dataframe['clean_text'].apply(
        lambda x: spacy_clean(x))
    dataframe = dataframe.dropna()
    dataframe['polarity_tokens'] = dataframe['clean_text'].map(
        lambda text: TextBlob(text).sentiment.polarity)
    dataframe['review_len'] = dataframe['clean_text'].astype(str).apply(len)
    dataframe['word_count'] = dataframe['clean_text'].apply(
        lambda word: len(str(word).split()))
    return dataframe
