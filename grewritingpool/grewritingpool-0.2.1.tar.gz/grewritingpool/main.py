import json
import logging
import random
import sys

import requests
from bs4 import BeautifulSoup as bs
from bs4 import element


def main(args):
    if len(args) == 1:
        if args[0] in ("-h", "--help"):
            print("grewriting [all|issue|argument]")
            sys.exit()
        else:
            _print_random_article(args[0])
    elif len(args) == 0:
        _print_random_article()
    else:
        print("grewriting [all|issue|argument]")
        sys.exit(1)


def _fetch_pool(writing_type):
    base_req = requests.get(
        "https://www.ets.org/gre/revised_general/prepare/analytical_writing/"+writing_type+"/pool")
    base_req.encoding = 'utf-8'
    base_res = base_req.text
    base_soup = bs(base_res, 'lxml')

    pool = []
    first_seperator = (base_soup.select("div.divider-50"))[0]
    status = 1
    tmp = {}
    for item in first_seperator.next_siblings:
        if isinstance(item, element.NavigableString):
            continue
        elif repr(item).startswith("<h2>"):
            break
        elif status == 1 and item.name == "p":
            tmp['first'] = item.contents[0]
            status = 2
        elif status == 2 and item.name == "p":
            tmp['second'] = item.contents[0]
            status = 2
        elif status == 2 and item.name == "div":
            status = 3
            tmp["instru"] = item.contents[1].contents[0]
            if item.contents[1].contents[0].name == "span":
                tmp["instru"] = item.contents[1].contents[0].contents[0]
        elif status == 3 and item.name == "div":
            tmp['type'] = writing_type
            pool.append(tmp)
            tmp = {}
            status = 1
    return json.dumps(pool)


def _fetch_type(fet):
    try:
        if fet in ("issue", "argument"):
            return _fetch_pool(fet)
        else:
            raise ValueError("Invalid Fetch Type "+fet+".")
    except ValueError as err:
        logging.exception(err)
        return json.dumps({"status": "invalid"})


def _random_article(writing_type):
    json_list = _fetch_type(writing_type)
    datalist = json.loads(json_list)
    secure_random = random.SystemRandom()
    writingitem = secure_random.choice(datalist)
    return writingitem


def _print_random_article(writing_type='default'):
    writingitem = ""
    if writing_type == 'default':
        writing_type = 'all'
        print("Writing type not set, default to 'all'...\n")
    try:
        if writing_type == 'all':
            secure_random = random.SystemRandom()
            writing_type = secure_random.choice(['argument', 'issue'])
            writingitem = _random_article(writing_type)
        elif writing_type in ('issue', 'argument'):
            writingitem = _random_article(writing_type)
        else:
            raise ValueError("Invalid Fetch Type "+writing_type+".")
    except ValueError as err:
        logging.exception(err)
    else:
        print(writingitem['type'].title() + ' Writing Pool\n')
        print('Question:')
        print(writingitem['first'])
        if 'second' in writingitem.keys():
            print('\n'+writingitem['second'])
        print('\nInstruction:')
        print(writingitem['instru'])
