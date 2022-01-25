import warnings
warnings.simplefilter("ignore")

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectFromModel, SelectKBest, mutual_info_classif
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC, LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion


def whitespace_tokenizer(s):
    """
    Split string on whitespace (e.g. when string is previously tokenized).
    """
    return s.split(" ")


class ModelNull(BaseEstimator):

    def fit(self, x, y):
        # Do nothing
        return self

    def transform(self, x):
        # Do nothing
        return x


class ModelStep:

    def __init__(self, name, model, label, params, estimator=None):
        self.name = name
        self.model = model
        self.label = label
        self.params = params
        self.estimator = estimator

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def get_step(self):
        if self.estimator:
            self.estimator = OneVsRestClassifier(self.estimator)
            return (self.name, self.model(self.estimator))
        else:
            return (self.name, self.model())

    def get_param(self):
        param_dict = {}
        for k in self.params:
            p_name = "{0}__{1}".format(self.name, k)
            p_value = self.params[k]
            param_dict[p_name] = p_value
        return param_dict


class ItemSelector(BaseEstimator, TransformerMixin):
    """For data grouped by feature, select subset of data at a provided key.
    The data is expected to be stored in a 2D data structure, where the first
    index is over features and the second is over samples.  i.e.
    >> len(data[key]) == n_samples
    Please note that this is the opposite convention to scikit-learn feature
    matrixes (where the first index corresponds to sample).
    ItemSelector only requires that the collection implement getitem
    (data[key]).  Examples include: a dict of lists, 2D numpy array, Pandas
    DataFrame, numpy record array, etc.
    >> data = {"a": [1, 5, 2, 5, 2, 8],
               "b": [9, 4, 1, 4, 1, 3]}
    >> ds = ItemSelector(key="a")
    >> data["a"] == ds.transform(data)
    ItemSelector is not designed to handle data grouped by sample.  (e.g. a
    list of dicts).  If your data is structured this way, consider a
    transformer along the lines of `sklearn.feature_extraction.DictVectorizer`.
    Parameters
    ----------
    key : hashable, required
        The key corresponding to the desired value in a mappable.
    Reference: http://scikit-learn.org/0.19/auto_examples/hetero_feature_union.html
    """
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]


class PipelineBuilder:

    def __init__(self):
        self.extractor_dict = {}
        self.classifier_dict = {}
        self.feature_selector_dict = {}
        self.analyzer_dict = {"word": "word", "char_wb": "char_wb"}
        self.tokenizer_dict = {"whitespace": whitespace_tokenizer, "none": None}
        self.extractor_op = None
        self.classifier_op = None
        self.analyzer_op = None
        self.tokenizer_op = None
        self.feature_selector_op = None

    def add_extractor(self, name, model, label, params):
        self.extractor_dict[label] = ModelStep(name, model, label, params)

    def add_classifier(self, name, model, label, params):
        self.classifier_dict[label] = ModelStep(name, model, label, params)

    def add_feature_selector(self, name, model, label, params, estimator=None):
        self.feature_selector_dict[label] = ModelStep(name, model, label, params, estimator=estimator)

    def get_analyzer_options(self):
        return list(self.analyzer_dict.keys())

    def get_tokenizer_options(self):
        return list(self.tokenizer_dict.keys())    

    def get_extractor_options(self):
        return list(self.extractor_dict.keys())

    def get_classifier_options(self):
        return list(self.classifier_dict.keys())

    def get_feature_selector_options(self):
        return list(self.feature_selector_dict.keys())

    def set_pipeline_options(self, extractor_op, classifier_op, analyzer_op, tokenizer_op):
        self.extractor_op = extractor_op
        self.classifier_op = classifier_op
        self.analyzer_op = analyzer_op
        self.tokenizer_op = tokenizer_op
        self.feature_selector_op = self.get_feature_selector_options()[0]

    def pipeline_representation(self):
        e = self.extractor_dict[self.extractor_op]
        c = self.classifier_dict[self.classifier_op]
        s = self.feature_selector_dict[self.classifier_op]
        rep = "{0} | {1} | {2}".format(e, c, s)
        return rep

    def build(self, fields):
        """
        Build model Pipeline and Grid Search params
        """
        params = {}
        # Field transform pipeline per field + params
        transformer_list = []

        for field in fields:
            pipe_key = "pipe_{}".format(field)
            steps = []    
            steps.append(tuple(["selector", ItemSelector(key=field)]))
            steps.append(self.extractor_dict[self.extractor_op].get_step())
            transformer_list.append(tuple([pipe_key, Pipeline(steps)]))
            # Nest params inside the union field - Extractor
            p_dict = self.extractor_dict[self.extractor_op].get_param()
            for k in p_dict:
                # Select analyzer param
                if k == "vectorizer__analyzer":
                    p_dict[k] = [self.analyzer_dict[self.analyzer_op]]
                # Select tokenizer param
                if k == "vectorizer__tokenizer":
                    p_dict[k] = [self.tokenizer_dict[self.tokenizer_op]]                
                new_k = "{}__{}__{}".format("union", pipe_key, k)
                params[new_k] = p_dict[k]

        # Classifier pipeline + params
        steps = []
        steps.append(tuple(["union", FeatureUnion(transformer_list=transformer_list)]))
        
        # Feature selector
        steps.append(self.feature_selector_dict[self.feature_selector_op].get_step())

        # Classifier
        steps.append(self.classifier_dict[self.classifier_op].get_step())

        pipe = Pipeline(steps)
        params.update(self.classifier_dict[self.classifier_op].get_param())

        return pipe, params


def get_vectorizers(pipe_builder):
    """
    Adds vectorizer options to PipelineBuilder object.
    """
    # analyzer options: wee keep this empty for now. will be populated on build
    analyzer_params = []
    # ngram length options (min, max)
    ngram_params = [(1, 2)]
    # minimum term frequency options
    min_df_params = [5]
    # use simple whitespace tokenizer because our data is already tokenized by MLP
    tokenizer_params = []
    # try both with and without idf component computed
    idf_params = [True, False]
    # params for hashing vectorizer
    hashing_params = {
        "ngram_range": ngram_params,
        "analyzer": analyzer_params,
        "tokenizer": tokenizer_params
    }
    pipe_builder.add_extractor("vectorizer", HashingVectorizer, "Hashing Vectorizer", hashing_params)
    # params for count vectorizer
    count_params = {
        "ngram_range": ngram_params,
        "min_df": min_df_params,
        "tokenizer": tokenizer_params,
        "analyzer": analyzer_params
    }
    pipe_builder.add_extractor("vectorizer", CountVectorizer, "Count Vectorizer", count_params)
    # params for tfidf vectorizer
    tfidf_params = {
        "ngram_range": ngram_params,
        "min_df": min_df_params,
        "tokenizer": tokenizer_params,
        "use_idf": idf_params,
        "analyzer": analyzer_params
    }
    pipe_builder.add_extractor("vectorizer", TfidfVectorizer, "TfIdf Vectorizer", tfidf_params)
    return pipe_builder


def get_classifiers(pipe_builder, workers):
    """
    Adds classifier options to PipelineBuilder object.
    """
    # we need multiprocessing to do this
    # use only if more workers, because it's a slow process
    if workers > 1:
        c_params = [0.1, 0.5, 1.0, 5.0, 10.0]
    else:
        c_params = [1.0]
    # logistic regression params
    logistic_params = {"solver": ["lbfgs"], "penalty": ["l2"], "C": c_params}
    pipe_builder.add_classifier("classifier", LogisticRegression, "Logistic Regression", logistic_params)
    # svm params
    svm_params = {"probability": [True], "kernel": ["linear"], "C": c_params}
    pipe_builder.add_classifier("classifier", SVC, "LinearSVC", svm_params)
    return pipe_builder


def get_pipeline_builder(workers=1):
    """
    Generates PipelineBuilder object with suitable options.
    """
    pipe_builder = PipelineBuilder()
    # get vectorizers
    pipe_builder = get_vectorizers(pipe_builder)
    # get classifiers
    pipe_builder = get_classifiers(pipe_builder, workers)
    # feature selector params
    pipe_builder.add_feature_selector(
        "feature_selector",
        SelectFromModel,
        "SVM Feature Selector",
        {},
        estimator=LinearSVC(penalty="l1", dual=False)
    )
    return pipe_builder
