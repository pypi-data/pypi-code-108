import operator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import logging
import requests
import pandas as pd

ops = {
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt
}


def get_conditional_phrases(conditions, phrase1, phrase2):
    bool_array = []
    for condition in conditions:
        for op in ops:
            if op in condition:
                splitted = condition.split(' ' + op + ' ')
                operator = ops[op]
                bool_array.append(operator(splitted[0], splitted[1]))
        # bool_array.append(eval(condition))
    if False in bool_array:
        return phrase2
    else:
        return phrase1


def get_random_synonymous(synonyms):
    random.seed()
    nKeys = len(synonyms.keys())
    pickedItem = random.randint(0, nKeys - 1)
    synPicked = synonyms[pickedItem]
    return synPicked


def words_to_digits(phrase):
    words = phrase.split(" ")
    num = []
    for word in words:
        if "." in word:
            word = word.replace(".", "")
        if "," in word:
            word = word.replace(",", "")
        if word.isdigit():
            num.append(int(word))
    return num


def add_random_synonymous_to_sentence(phrase, placeholder, synonyms):
    random.seed()
    nKeys = len(synonyms.keys())
    pickedItem = random.randint(0, nKeys - 1)
    synPicked = synonyms[pickedItem]
    phrase = phrase.replace(placeholder, synPicked)
    return phrase


def text_from_data(df, examples=None, max_tokens=64, fit_items=True):
    # The parameter "df" is a dataframe, but it will be converted into a dict, and called df in each case

    if examples is None:
        examples = [["player=Cristiano Ronaldo, goals=10, team=Juventus", "Cristiano Ronaldo scored 10 goals for Juventus"]]
        print("Using a default example: \n" + str(examples) + "\n")

    if not df.empty:
        headers = {
            "Content-Type": "application/json"
        }

        dict_df = df.to_dict()

        data = {
            "df": dict_df,
            "examples": examples,
            "fit_items": fit_items,
            "max_tokens": max_tokens
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = "https://api-dev.askdata.com/cfc/nlg"

        r = s.post(url=url, headers=headers, json=data)
        r.raise_for_status()

        try:
            df_response = pd.DataFrame.from_dict(r.json()['dict_df'])
            return df_response
        except Exception as e:
            logging.error(str(e))
    else:
        print("Input DataFrame is empty!")
        df_response = pd.DataFrame()
        return df_response
