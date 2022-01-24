
import os
import spacy

from depronounize.pronouns_gender_number import \
  PLURAL_PRONOUNS, SINGULAR_PRONOUNS,\
  MASCULINE_PRONOUNS, FEMININE_PRONOUNS

from depronounize.masculine import masculine  # list of masculine nouns/names lower-case
from depronounize.feminine import feminine  # list of feminine nouns/names lower-case


# Setup Spacy
if not spacy.util.is_package('en_core_web_sm'):
    os.system("python -m spacy download en_core_web_sm")

nlp = spacy.load('en_core_web_sm')  # md / sm


# Global vars
NUM_NOUNS = 5
nouns_stack = []
pronouns_to_ignore = ['i', 'you', 'he', 'she']


def is_masculine(token):
    return token.text.lower() in masculine


def is_feminine(token):
    return token.text.lower() in feminine


def add_to_nouns(token):
    global nouns_stack
    if len(nouns_stack) > NUM_NOUNS - 1:
        del(nouns_stack[NUM_NOUNS:])
    nouns_stack.insert(0, token)


def get_matching_noun(pronoun):
    """
    @arg: pronoun token
    return: noun token if found, else same pronoun token
    """
    pron_is_plur = pronoun.text.lower() in PLURAL_PRONOUNS
    pron_is_sing = pronoun.text.lower() in SINGULAR_PRONOUNS
    pron_is_masc = pronoun.text.lower() in MASCULINE_PRONOUNS
    pron_is_fem = pronoun.text.lower() in FEMININE_PRONOUNS

    for noun_token in nouns_stack:
        noun_is_plur = (noun_token.text.lower()[-1] == 's') and \
            (noun_token.lemma_[-1] != 's')
        noun_is_masc = is_masculine(noun_token)
        noun_is_fem = is_feminine(noun_token)
        # match number
        if (noun_is_plur and not pron_is_sing) or \
           (not noun_is_plur and not pron_is_plur):
            # match gender
            if (noun_is_masc and not pron_is_fem) or \
               (noun_is_fem and not pron_is_masc) or \
               (not noun_is_fem and not noun_is_masc):
                return noun_token

    return pronoun


def replace_pronouns(in_text):
    global nouns_stack
    tokens = nlp(in_text)
    out_tokens = []
    for idx in range(len(tokens)):
        token = tokens[idx]
        # Add proper nouns and nouns to queue
        if token.pos_ in [u'NOUN', u'PROPN']:
            add_to_nouns(token)
        # Replace pronoun if possible
        if token.pos_ == u'PRON' and \
           token.text.lower() not in pronouns_to_ignore:
            out_tokens.append(get_matching_noun(token))
        else:
            out_tokens.append(token)

    out_strings = [t.text for t in out_tokens]
    return ' '.join(out_strings)

