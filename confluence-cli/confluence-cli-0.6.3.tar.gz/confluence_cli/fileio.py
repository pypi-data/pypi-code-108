import ast
import csv
import logging
from typing import List, Dict

from requests import Response

logger = logging.getLogger("confluence_log")


def save_csv(elements: List[dict], filename: str, fields: List[str] = None, header: bool = False):
    if elements:
        fields = fields if fields else list(elements[0].keys())
        # if isinstance(elements[0], NavigableDict):
        #    elements = [navigable_to_dict(element) for element in elements]
    else:
        logger.debug("No elements to save to CSV, returning")
        return
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        logger.debug(f"Saving {len(elements)} rows to csv file '{filename}'")
        if header:
            writer.writeheader()
        writer.writerows(elements)


def rows2csv(rows, filename):
    if not filename:
        logger.debug("rows2csv: No filename to print to. exiting")
        return
    if not rows:
        logger.debug("rows2csv: No rows to print. exiting")
        return

    with open(filename, 'w', newline='\n', encoding='utf-8') as file:
        writer = csv.writer(file)
        if rows:
            writer.writerows(rows)


def load_csv(csv_file, header: bool = False, eval: bool = False) -> List[Dict]:
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        if header:
            next(reader)
        dict_lst = [d for d in reader]
        if eval:
            for d in dict_lst:
                for k, v in d.items():
                    try:
                        d[k] = ast.literal_eval(str(v))
                        logger.debug(f"eval done: {d[k]}")
                    except (ValueError, SyntaxError):
                        continue
        return dict_lst


def print_csv(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        logger.debug("\n*********** {} **************".format(filename))
        for line in reader:
            logger.debug(line)


def utf16_response_to_csv(resp: Response, outfilename):
    decoded_content = resp.content.decode('utf-16')
    csvr = csv.reader(decoded_content.splitlines(), delimiter=',')

    with open(outfilename, 'w', newline='\n', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in csvr:
            writer.writerow(row)
    # if logger.isEnabledFor(logging.DEBUG):
    #     print_csv(outfilename)
