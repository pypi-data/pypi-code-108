import random
import json
import logging

import grewritingpool.main as gwp

def get_list(writing_type = "dafault"):
    """
    get a list of all or certain writing type.

    :param writing_type: Type of writing, leave blank for all. [all,argument,issue]
    :return: A json array of all or certain writing type.
    :raise ValueError: A error occured when fetch writing type is invalid.
    """
    try:
        if writing_type == 'default':
            writing_type = 'all'
        if writing_type == 'all':
            return json.dumps(json.loads(gwp._fetch_type('argument'))+json.loads(gwp._fetch_type('issue')))
        elif writing_type in ('argument', 'issue'):
            return gwp._fetch_type(writing_type)
        else:
            raise ValueError("Invalid Fetch Type "+writing_type+".")
    except ValueError as err:
        logging.exception(err)

def get_random(writing_type = 'default'):
    """
    get a json list of all or certain writing type.

    :param writing_type: Type of writing, leave blank for all. [all,argument,issue]
    :return: A jsonstring of one writing question.
    """
    if writing_type == 'default':
        writing_type = 'all'
    if writing_type == 'all':
        secure_random = random.SystemRandom()
        writing_type = secure_random.choice(['argument','issue'])
    return gwp._random_article(writing_type)