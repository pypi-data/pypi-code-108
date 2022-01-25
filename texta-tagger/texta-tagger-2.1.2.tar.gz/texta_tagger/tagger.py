from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score, accuracy_score, jaccard_score
import pandas as pd
import numpy as np
import zipfile
import joblib
import json
import re

from texta_tools.text_processor import TextProcessor
from typing import List, Union
from .pipeline import get_pipeline_builder
from .tagging_report import TaggingReport
from . import exceptions

ENABLED_METRICS = ["precision", "recall", "f1_score", "jaccard", "accuracy"]

def check_model_loaded(func):
    """
    Wrapper function for checking if Tagger model is loaded.
    """
    def func_wrapper(*args, **kwargs):
        if not args[0].model:
            raise exceptions.ModelNotLoadedError()
        return func(*args, **kwargs)
    return func_wrapper



class Tagger:

    pipeline = get_pipeline_builder()
    CLASSIFIERS = pipeline.get_classifier_options()
    VECTORIZERS = pipeline.get_extractor_options()
    ANALYZERS = pipeline.get_analyzer_options()
    TOKENIZERS = pipeline.get_tokenizer_options()

    def __init__(self, workers=1, description="Tagger", embedding=None, mlp=None, custom_stop_words=[], ignore_numbers=False, ignore_punctuation=True,
                 test_size=0.2, classifier=CLASSIFIERS[0], vectorizer=VECTORIZERS[0], max_examples_per_class=10000, feature_hashing=False,
                 analyzer=ANALYZERS[0], tokenizer=TOKENIZERS[0]):
        # resulting objects etc.
        self.model = None
        self.report = None
        self.tagger_django_model = None
        # options
        self.classifier = classifier
        self.vectorizer = vectorizer
        self.analyzer = analyzer
        self.tokenizer = tokenizer
        self.workers = workers
        self.test_size = test_size
        self.description = description
        self.max_examples_per_class = max_examples_per_class
        self.feature_hashing = feature_hashing

        # check embedding for phraser
        phraser = None
        if embedding:
            phraser = embedding.phraser
        
        # set text processor
        self.text_processor = TextProcessor(
            phraser=phraser,
            lemmatizer=mlp,
            custom_stop_words=custom_stop_words,
            ignore_numbers=ignore_numbers,
            ignore_punctuation=ignore_punctuation,
            text_hashing=feature_hashing)
        
        # set default sklearn average functions
        self.sklearn_average_binary = "binary"
        self.sklearn_average_multilabel = "micro"
        self.scoring_function = None
        # metrics map for make_scorer
        self.metric_map = {
            "precision": {"function": precision_score, "needs_pos_label": True},
            "recall": {"function": recall_score, "needs_pos_label": True},
            "f1_score": {"function": f1_score, "needs_pos_label": True},
            "jaccard": {"function": jaccard_score, "needs_pos_label": True},
            "accuracy": {"function": accuracy_score, "needs_pos_label": False},
        }


    def __str__(self):
        return self.description


    def _get_scorer(self, metric: str, pos_label: Union[str, int], average: str):
        """
        Make custom scorer based on given metric function.
        :param str metric: Metric to use in the custom scorer. Available choices: all metrics in self.metric_map.
        :param str/int pos_label: Positive label in binary taggers.
        :param str average: Average function to use in cutom scorer.
        """
        custom_scorer = None
        if metric:
            if metric not in self.metric_map:
                raise exceptions.InvalidScoringIdentifierError(f"Metric identifier'{metric}' is not in the list of available metrics. Available metrics: {list(self.metric_map.keys())}")
            # Retrieve params related to the chosen metric
            metric_data = self.metric_map[metric]
            if metric_data["needs_pos_label"]:
                custom_scorer = make_scorer(metric_data["function"], greater_is_better=True,  pos_label=pos_label, average=average)
                self.scoring_function = f"{metric}_{average}"
            else:
                custom_scorer = make_scorer(metric_data["function"], greater_is_better=True)
                self.scoring_function = metric
        return custom_scorer


    def _get_pos_label(self, labels: List[Union[str, int]], pos_label: Union[str, int]) -> Union[str, int]:
        if not pos_label:
            if len(labels) == 2:
                if "true" in labels:
                    pos_label = "true"
                else:
                    raise exceptions.PosLabelNotSpecifiedError("Label set must contain label 'true' or positive label must be specified.")
            else:
                # Pos label is not important on multilabel dataset
                pos_label = None
        return pos_label


    @staticmethod
    def _texts_to_documents(texts):
        """
        Transforms list of texts into list of documents.
        """
        return [{"text": text} for text in texts]


    @staticmethod
    def _validate_data_sample(data_sample):
        if not isinstance(data_sample, dict) or not data_sample:
            raise exceptions.InvalidInputError("Input data sample should be a non-empty dictionary.")
        data_sample_values = list(data_sample.values())
        if not isinstance(data_sample_values[0], list) or not data_sample_values[0]:
            raise exceptions.InvalidInputError("Data sample values should be non-empty lists.")
        data_sample_first_value = data_sample_values[0][0]
        if not isinstance(data_sample_first_value, str) and not isinstance(data_sample_first_value, dict):
            raise exceptions.InvalidInputError(f"Data sample values should contain list of dicts or list of strings. Instead it is {type()}")


    def train(self, data_sample, field_list=[], scoring=None, pos_label=None, sklearn_average=None):
        """
        Executes the pipeline and trains one vs rest classification model based on data sample.
        :param dict data_sample: Dict containing training data. Dict keys are labels and values are either lists of texts or list of documents.
        :param list field_list: List of fieldnames used in training the model, e.g. ["text"].
        """
        # check if data sample is valid
        self._validate_data_sample(data_sample)
        # limit data sample size
        data_sample = {k:v[:self.max_examples_per_class] for k,v in data_sample.items()}
        # if input is strings (texts) instead of dictionaries (documents), create documents
        if isinstance(list(data_sample.values())[0][0], str):
            data_sample = {k: self._texts_to_documents(v) for k,v in data_sample.items()}
        # if no field list, default to all fields in the first document.
        if not field_list:
            field_list = list(list(data_sample.values())[0][0].keys())

        # get labels
        labels = list(data_sample.keys())
        # get positive label
        pos_label = self._get_pos_label(labels, pos_label)
        # set average_function:
        if not sklearn_average:
            if len(labels) == 2:
                sklearn_average = self.sklearn_average_binary
            else:
                sklearn_average = self.sklearn_average_multilabel
        # get custom scorer:
        scorer = self._get_scorer(scoring, pos_label, sklearn_average)
        # pipeline
        pipe_builder = get_pipeline_builder(workers=self.workers)
        pipe_builder.set_pipeline_options(self.vectorizer, self.classifier, self.analyzer, self.tokenizer)
        c_pipe, c_params = pipe_builder.build(fields=field_list)
        # build data map
        data_sample_x_map = {}
        data_sample_y = []
        for label, class_examples in data_sample.items():
            # creates dict containing field name as key and list of field values as value
            example_map = self._create_data_map(class_examples, field_list)
            # build x feature map and label list
            for field in field_list:
                if field not in data_sample_x_map:
                    data_sample_x_map[field] = []
                data_sample_x_map[field] += example_map[field]
            data_sample_y = data_sample_y + [label] * len(class_examples)
        X_train = {}
        X_test = {}
        #  split data
        for field in field_list:
            X_train[field], X_test[field], y_train, y_test = train_test_split(data_sample_x_map[field], data_sample_y, test_size=self.test_size, random_state=42)
        # dataframes
        df_train = pd.DataFrame(X_train)
        df_test = pd.DataFrame(X_test)

        # Use Train data to parameter selection in a Grid Search
        gs_clf = GridSearchCV(c_pipe, c_params, n_jobs=self.workers, cv=5, verbose=False, scoring=scorer)
        gs_clf = gs_clf.fit(df_train, y_train)
        model = gs_clf.best_estimator_
        # Use best model and test data for final evaluation
        y_pred = model.predict(df_test)
        # calculate y scores
        y_scores = model.decision_function(df_test)
        # get number of features
        num_features = len(model.named_steps["feature_selector"].get_support())
        # Report model statistics
        report = TaggingReport(
            y_test,
            y_pred,
            y_scores,
            num_features,
            {k:len(v) for k,v in data_sample.items()},
            labels,
            pos_label
        )
        # update model & report
        self.model = model
        self.report = report
        return report


    @check_model_loaded
    def get_feature_coefs(self):
        """
        Return feature coefficients for a given model.
        """
        coef_matrix = self.model.named_steps["classifier"].coef_
        # transform matrix if needed
        if type(coef_matrix) == np.ndarray:
            feature_coefs = coef_matrix[0]
        else:
            feature_coefs = coef_matrix.todense().tolist()[0]
        return list(feature_coefs)


    @check_model_loaded
    def get_feature_names(self):
        """
        Returns feature names for a given model.
        Does not work with Hashing Vectorizer.
        """
        if self.vectorizer == "Hashing Vectorizer":
            raise exceptions.NotSupportedError("This feature is not supported with Hashing Vectorizer")
        return self.model.named_steps["union"].transformer_list[0][1].named_steps["vectorizer"].get_feature_names()


    @check_model_loaded
    def get_supports(self):
        """
        Returns supports for a given model.
        """
        return self.model.named_steps["feature_selector"].get_support()


    @check_model_loaded
    def get_features(self):
        """
        Returns features with coefs for a given model.
        """
        features = self.get_feature_names()
        feature_coefs = self.get_feature_coefs()
        supports = self.get_supports()
        selected_features = [feature for i, feature in enumerate(features) if supports[i]]
        selected_features = [{'feature': feature, 'coefficient': feature_coefs[i]} for i, feature in enumerate(selected_features) if feature_coefs[i] > 0]
        selected_features = sorted(selected_features, key=lambda k: k['coefficient'], reverse=True)
        return selected_features


    @check_model_loaded
    def get_fields_from_model(self):
        """
        Returns field names the model was trained on.
        """
        # retrieve field names from the model
        union_features = [x[0] for x in self.model.named_steps["union"].transformer_list if x[0].startswith("pipe_")]
        field_features = [x[5:] for x in union_features]
        return field_features


    @check_model_loaded
    def save(self, file_path):
        """
        Saves tagger model to disk.
        :param str file_path: Path to the model file.
        """
        joblib.dump(self.model, file_path)
        return True


    def load(self, file_path):
        """
        Loads model from disk.
        :param str file_path: Path to the model file.
        """
        self.model = joblib.load(file_path)
        return True


    def load_django(self, tagger_django_object):
        """
        Loads model file using Django model object. This method is used in Django only!
        :param tagger_django_object: Django model object of the Tagger.
        """
        try:
            tagger_path = tagger_django_object.model.path
            # retrieve tagger info
            self.description = tagger_django_object.description
            self.classifier = tagger_django_object.classifier
            self.vectorizer = tagger_django_object.vectorizer
            # retrieve and update stop custom stop words in text processor
            self._add_custom_stop_words(tagger_django_object.stop_words)
            # load model
            return self.load(tagger_path)
        except:
            raise exceptions.ModelLoadFailedError()


    def load_zip(self, zip_path):
        """
        Loads model from ZIP file generated in Django.
        :param: str zip_path: Location of the ZIP file.
        """
        if not zipfile.is_zipfile(zip_path):
            raise exceptions.InvalidInputError("This is not a ZIP file")

        try:
            zip_ref = zipfile.ZipFile(zip_path, "r")
            # find files of interest
            zip_content = zip_ref.namelist()
            json_file = [f for f in zip_content if f == "model.json"][0]
            model_file = [f for f in zip_content if f.startswith("tagger_")][0]
            # retrieve tagger info
            tagger_info = json.loads(zip_ref.read(json_file))
            self.description = tagger_info["description"]
            self.classifier = tagger_info["classifier"]
            self.vectorizer = tagger_info["vectorizer"]
            # retrieve and update stop custom stop words in text processor
            self._add_custom_stop_words(tagger_info["stop_words"])
            # load model
            self.model = joblib.load(zip_ref.open(model_file))
            return True
        except:
            raise exceptions.ModelLoadFailedError()


    @check_model_loaded
    def tag_text(self, text):
        """
        Predicts on raw text
        :param str text: Input text as string.
        """
        # retrieve field names from the model
        field_features = self.get_fields_from_model()
        # process text
        text = self.text_processor.process(text)
        # generate text map for dataframe
        text_map = {feature_name:[text] for feature_name in field_features}
        df_text = pd.DataFrame(text_map)
        return self._process_prediction_output(self.model.predict(df_text)[0], max(self.model.predict_proba(df_text)[0]))


    @check_model_loaded
    def tag_doc(self, doc):
        """
        Predicts on json document
        :param str text: Input doc as dictionary.
        """
        if not isinstance(doc, dict):
            raise exceptions.InvalidInputError(f"Input should be a dictionary, instead it is {type(doc)}")
        # retrieve field names from the model
        field_features = self.get_fields_from_model()
        # generate text map for dataframe
        text_map = {}
        for field in field_features:
            if field in doc:
                # process text
                processed_field = self.text_processor.process(doc[field])
                text_map[field] = [processed_field]
            else:
                text_map[field] = [""]
        df_text = pd.DataFrame(text_map)
        return self._process_prediction_output(self.model.predict(df_text)[0], max(self.model.predict_proba(df_text)[0]))


    @staticmethod
    def _process_prediction_output(predicted_label, probability):
        return {
            "prediction": predicted_label,
            "probability": probability
        }


    def _load_stop_words_from_string(self, stop_words_string: str) -> List[str]:
        """
        Loads stop words from whitespace-separated string into list.
        """
        stop_words = re.split(" |\n|\r\n", stop_words_string)
        stop_words = [stop_word for stop_word in stop_words if stop_word]
        return stop_words


    def _add_custom_stop_words(self, stop_words: str):
        """
        Splits string of stop words by space or newline and removes empties.
        Updates current TextProcessor custom stop words.
        """
        try:
            stop_words = json.loads(stop_words)
        except:
            stop_words = self._load_stop_words_from_string(stop_words)
        self.text_processor.custom_stop_words = stop_words


    def _create_data_map(self, data, field_list):
        """
        Creates data map where fields are filtered by the field list - fields not present in list will be ignored.
        """
        data_map = {field: [] for field in field_list}
        for document in data:
            for field in field_list:
                if field in document:
                    processed = self.text_processor.process(document[field])
                    data_map[field].append(processed)
                else:
                    data_map[field].append("")
        return data_map
