'''
Author: Alberto Rubiales Borrego
Mail: al.rubiales.b@gmail.com
Github: arubiales
Created Date: 24-Jan-2022
-----
Last Modified: 24-Jan-2022
Modified By: Alberto Rubiales Borrego
-----
'''
from utils import tqdm_manager
from typing import List, Callable
import spacy


class SentenceEDA:
    """
    It's an EDA Manager that you can add functions to create pipelines. In order to do EDA clear and efficient.

    Parameters
    -----------
    corpus: a list of strings to apply the functions
    funcs_to_map: The functions to map to the corpus

    Methods
    --------
    fit: Execute all the functions added
    """

    def __init__(self, corpus: list, funcs_to_map: list) -> None:
        self.corpus = corpus
        self.funcs_to_map = funcs_to_map
        self.result_per_func = []

    def fit(self) -> List[List]:
        """
        Compute all EDA functions added

        Returns:
        A list of list with the result of every function
        """
        for func in self.funcs_to_map:
            self.result_per_func.append(func(self.corpus))
        return self.result_per_func


class FeatureEnginieringNLP:
    """
    Create 3 new variables from NLP, The token, the lemma and the POS. (This functions use a lot of resouces and can be
    computationally expensive)

    Parameters
    -----------
    model: str
        The NLP pretrained model to use

    functions: list[str] = ["token", "lemma", "pos"]
        The operations to perform to a corpus. The operations availables are:
            - token: tokenization
            - lemma: lemmatization
            - pos: Part Of Speech

    Methods
    --------
    fit: compute the functions selected in `self.functions`
    """

    def __init__(
        self,
        model: str = "en_core_web_trf",
        functions: Callable = ["token", "lemma", "pos"],
    ):
        self.functions = functions
        self.nlp = spacy.load(model)

    def _check_func(self, func: Callable, doc: str):
        """
        Check what is the function in order to return the proper result

        Arguments
        ----------
        func: str
            The function to check
        doc: str
            The sentence to apply the function

        Returns
        --------
            The result of compute `func` to the `sentence`
        """
        if func == "token":
            return [word for word in doc]
        elif func == "lemma":
            return [word.lemma_ for word in doc]
        return [word.pos_ for word in doc]

    def fit(self, corpus: List[str], verbose: bool = True):
        """
        Compute the functions selected in `self.functions`

        Arguments:
        -----------
        corpus: list[str]
            All the sentences to compute the operations

        verbose: Bool
            Run with verbose or not (tqdm)

        Returns
        --------
        A dictionary using `self.functions` as a key and the result  of the operation as a value
        """
        nlp_parse = tqdm_manager(corpus, self.nlp, verbose)

        results = {"nlp": nlp_parse}

        for func in self.functions:
            result_per_func = []
            for sentence in nlp_parse:
                result_per_func.append(self._check_func(func, sentence))
            results[func] = result_per_func
        return results
