import sys
from wora.file import read_file
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English
import regex as re

nlp = English()
tokenizer = Tokenizer(nlp.vocab)

def parse(cont: list) -> dict:
    ''' Parses a list and returns a dictionary of
    containing the string effect to apply, and the text
    to which it is applied to
    '''
    tokens = {}
    regex = r'(.*?)(?=\])'

    i = 0
    keyword = ''
    start1 = 0
    start2 = 0
    end = 0
    while i < len(cont):
        x = cont[i]
        if x == '[':
            if re.match(re.compile('/'), cont[i+1]):
                tokens[keyword] = cont[start1+2:start2+1]
        else:
            if (start1 == 0):
                start1 = i
                keyword = cont[i]
            else:
                start2 = i
        if x == ']':
            end = i
        i += 1
    return tokens

def get_tokens(fp: str):
    ''' Creates a list of tokens from the contents of a file '''
    conts = read_file(fp)
    my_doc = nlp(conts)

    token_list = []
    for token in my_doc:
        token_list.append(token.text)
    return token_list

def to_string(token_dict: dict):
    ''' Converts a list of tokens into a string '''
    string = ''
    i = 0
    for vals in token_dict.values():
        if (vals != '\n'):
            string += ' '.join(vals)
        else:
            string += '\n'
        i+=1
    return string

def parse_transforms(fp: str):
    '''
    Returns a dictionary of tokens with an effect and the text which it is applied to
    '''
    tokens: list = get_tokens(fp)
    token_dict: dict = parse(tokens)
    return token_dict
