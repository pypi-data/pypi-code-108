import os
import re, json, jsonlines
from collections import OrderedDict, defaultdict
from typing import List, Union
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

porter_stemmer = PorterStemmer()
s_words = set(stopwords.words("english"))


def calc_f1(precision: float, recall: float):
    """Calculates the F1 score

    Args:
        precision (float): The calculated precision
        recall (float): The calculated recall

    Returns:
        float: The F1 score
    """
    
    if precision + recall == 0:
        return 0
    return 2 * ((precision * recall) / (precision + recall))


def calc_acc(pred_data: List[List[str]], gold_data: List[List[str]]):
    """Calculates the accuracy, precision and recall

    Args:
        pred_data (List[List[str]]): The output data from the model
        gold_data (List[List[str]]): The labeled data to compare with

    Returns:
        tuple[float, float, float]: Accuracy, recall and precision of the predictions
    """

    nr_dp = len(pred_data)
    nr_correct = 0
    nr_min_one_corr = 0
    total_pred = 0
    total_gold = 0
    for i, pred_list in enumerate(pred_data):
        min_one_corr = False
        for pred_d in pred_list:
            total_pred += 1
            total_gold += len(gold_data[i])
            if pred_d in gold_data[i]:
                nr_correct += 1
                min_one_corr = True
        if min_one_corr:
            nr_min_one_corr += 1

    accuracy = nr_min_one_corr / nr_dp
    recall = nr_correct / total_gold
    precision = nr_correct / total_pred
    return accuracy, recall, precision


def create_dirs_if_not_exist(path: str):
    """Create the directory where the path points to.
    Does nothing if the dir already exists

    Args:
        path (str): Either a path to a directory or a file
    """

    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def load_json(path: str):
    """Loads the json file from 'path' into a list of dicts

    Args:
        path (str): The path to the json file

    Raises:
        ValueError: If the provided path does not point to a json file

    Returns:
        dict: A dict of the json file
    """

    if not ".json" in path:
        raise ValueError("'path' is not pointing to a json file")
    data = None
    with open(path) as f:
        data = json.loads(f.read())
    return data


def load_jsonl(path: str) -> List[dict]:
    """Loads the jsonl file from 'path' into a list of dicts

    Args:
        path (str): The path to the jsonl file

    Raises:
        ValueError: If the provided path does not point to a jsonl file

    Returns:
        List[dict]: A list of the jsonl file
    """

    if not ".jsonl" in path:
        raise ValueError("'path' is not pointing to a jsonl file")
    result = []
    with jsonlines.open(path) as reader:
        for doc in reader:
            result.append(doc)
    return result


def store_json(
    data: Union[dict, list, defaultdict, OrderedDict],
    file_path: str,
    sort_keys=False,
    indent=2,
):
    """ Function for storing a dict to a json file. 
        Will create the directories in the path if they don't
        already exist.

    Args:
        data (dict): The dict or list to be stored in the json file
        file_path (str): The path to the file to be created (note: will delete files that have the same name)
        sort_keys (bool, optional): Set to True if the keys in the dict should be sorted before stored (default: False)
        indent (bool, optional): Set this if indentation should be added (default: None)

    Raises:
        ValueError: If the input datatype is not correct or the file path does not point to a json file
    """

    if (
        type(data) != dict
        and type(data) != list
        and type(data) != defaultdict
        and type(data) != OrderedDict
    ):
        raise ValueError("'data' needs to be a dict")
    if ".json" not in file_path:
        raise ValueError("'file_path' needs to include the name of the output file")
    create_dirs_if_not_exist(file_path)
    with open(file_path, mode="w") as f:
        f.write(json.dumps(data, sort_keys=sort_keys, indent=indent))


def store_jsonl(data: list, file_path: str):
    """ Function for storing a list as a jsonl file.
        Will create the directories in the path if they don't
        already exist.

    Args:
        data (list): A list of arbitrary type
        file_path (str): The path to the file to be created (note: will delete files that have the same name)

    Raises:
        ValueError: If the input datatype is not correct or the file path does not point to a jsonl file
    """
    
    if type(data) != list:
        raise ValueError("'data' needs to be a list")
    if ".jsonl" not in file_path:
        raise ValueError("'file_path' needs to include the name of the output file")
    create_dirs_if_not_exist(file_path)
    with jsonlines.open(file_path, mode="w") as f:
        for d in data:
            f.write(d)


def stemming_tokenizer(input: str):
    """Converts a string to a list of words, removing special character, stopwords
        and stemming the words

    Args:
        input (str): The string to be tokenized

    Returns:
        list: A list of words
    """

    words = re.sub(r"[^A-Za-z0-9\-]", " ", input).lower().split()
    words = [word for word in words if word not in s_words]
    words = [porter_stemmer.stem(word) for word in words]
    return words


def tokenize(s: str):
    """Converts a string to a list of words, and removing special character and stopwords

    Args:
        s (str): The string to be tokenized

    Returns:
        list: A list of words
    """

    words = re.sub(r"[^A-Za-z0-9\-]", " ", s).lower().split()
    words = [word for word in words if word not in s_words]
    return words


def unique(sequence: list):
    """Returns all the unique items in the list while keeping order (which set() does not)

    Args:
        sequence (list): The list to filter

    Returns:
        list: List with only unique elements
    """
    
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]
