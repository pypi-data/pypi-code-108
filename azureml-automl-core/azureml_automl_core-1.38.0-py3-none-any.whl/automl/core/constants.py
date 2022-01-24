# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines constants used in AutoML in Azure Machine Learning.

To learn about AutoML in Azure Machine Learning, see [What is automated machine
learning?](https://docs.microsoft.com/azure/machine-learning/concept-automated-ml).
For more information about using constants defined in this module, see [Configure
automated ML experiments](https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train).
"""


class FeaturizationConfigMode:
    """Defines featurization modes that are used in AutoML.

    In typical use cases, you specify featurization in the :class:`azureml.train.automl.automlconfig.AutoMLConfig`
    with the ``featurization`` parameter.
    """
    Auto = 'auto'
    Off = 'off'
    Customized = 'customized'


class FeatureType:
    """Defines names of feature types that are recognized for feature engineering in AutoML.

    In typical use cases, you use FeatureType attributes for customizing featuration with the
    :class:`azureml.train.automl.automlconfig.AutoMLConfig` class and the ``featurization`` parameter.

    .. remarks::

        FeatureType attributes are used when customizing featurization. For example, to update a
        column type, use the :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig`
        class as shown in the example.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.add_column_purpose('column1', 'Numeric')
            featurization_config.add_column_purpose('column2', 'CategoricalHash')

        For more information, see `Configure automated ML experiments
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.
    """

    Numeric = 'Numeric'
    DateTime = 'DateTime'
    Categorical = 'Categorical'
    CategoricalHash = 'CategoricalHash'
    Text = 'Text'
    Hashes = 'Hashes'
    Ignore = 'Ignore'
    AllNan = 'AllNan'

    FULL_SET = {Numeric, DateTime, Categorical, CategoricalHash, Text, Hashes, Ignore, AllNan}

    # List of features types that are dropped and not featurized
    DROP_SET = {Hashes, Ignore, AllNan}


class _FeaturizersType:
    """Names for featurizer factory types"""
    Numeric = 'numeric'
    DateTime = 'datetime'
    Categorical = 'categorical'
    Text = 'text'
    Generic = 'generic'


class SupportedTransformers:
    """Defines customer-facing names for transformers supported by AutoML.

    Transformers are classified for use with
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.Categorical`
    data (e.g., ``CatImputer``),
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.DateTime`
    data (e.g., ``DataTimeTransformer``),
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.Text`
    data (e.g., ``TfIdf``), or for
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.Generic`
    data types (e.g., ``Imputer``).

    .. remarks::

        The attributes defined in SupportedTransformers are used in featurization summaries when using
        `automatic preprocessing in automated ML
        <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml#preprocess>`_
        or when customizing featurization with the
        :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class
        as shown in the example.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.add_transformer_params('Imputer', ['column1'], {"strategy": "median"})
            featurization_config.add_transformer_params('HashOneHotEncoder', [], {"number_of_bits": 3})

        For more information, see `Configure automated ML experiments
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.

    Attributes:
        ImputationMarker: Add boolean imputation marker for imputed values.

        Imputer: Complete missing values.

        MaxAbsScaler: Scale data by its maximum absolute value.

        CatImputer: Impute missing values for categorical features by the most frequent category.

        HashOneHotEncoder: Convert input to hash and encode to one-hot encoded vector.

        LabelEncoder: Encode categorical data into numbers.

        CatTargetEncoder: Map category data with averaged target value for regression and to the class probability
            for classification.

        WoETargetEncoder: Calculate the Weight of Evidence of correlation of a categorical data to a target column.

        OneHotEncoder: Convert input to one-hot encoded vector.

        DateTimeTransformer: Expand datatime features into sub features such as year, month, and day.

        CountVectorizer: Convert a collection of documents to a matrix of token counts.

        NaiveBayes: Transform textual data using sklearn Multinomial Naïve Bayes.

        StringCast: Cast input to string and lower case.

        TextTargetEncoder: Apply target encoding to text data where a stacked linear model with bag-of-words
            generates the probability of each class.

        TfIdf: Transform a count matrix to a normalized TF or TF-iDF representation.

        WordEmbedding: Convert vectors of text tokens into sentence vectors using a pre-trained model.

        CUSTOMIZABLE_TRANSFORMERS: Transformers that are customized in featurization with parameters of methods
            in the :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class.

        BLOCK_TRANSFORMERS: Transformers that can be blocked from use in featurization in the
            :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class.

        FULL_SET: The full set of transformers.
    """

    # Generic
    ImputationMarker = 'ImputationMarker'
    Imputer = 'Imputer'
    MaxAbsScaler = 'MaxAbsScaler'

    # Categorical
    CatImputer = 'CatImputer'
    HashOneHotEncoder = 'HashOneHotEncoder'
    LabelEncoder = 'LabelEncoder'
    CatTargetEncoder = 'CatTargetEncoder'
    WoETargetEncoder = 'WoETargetEncoder'
    OneHotEncoder = 'OneHotEncoder'

    # DateTime
    DateTimeTransformer = 'DateTimeTransformer'

    # Text
    CountVectorizer = 'CountVectorizer'
    NaiveBayes = 'NaiveBayes'
    StringCast = 'StringCast'
    TextTargetEncoder = 'TextTargetEncoder'
    TfIdf = 'TfIdf'
    WordEmbedding = 'WordEmbedding'

    CUSTOMIZABLE_TRANSFORMERS = {
        HashOneHotEncoder,
        Imputer,
        TfIdf
    }

    BLOCK_TRANSFORMERS = {
        HashOneHotEncoder,
        LabelEncoder,
        CatTargetEncoder,
        WoETargetEncoder,
        OneHotEncoder,
        CountVectorizer,
        NaiveBayes,
        TextTargetEncoder,
        TfIdf,
        WordEmbedding
    }

    FULL_SET = {
        ImputationMarker,
        Imputer,
        MaxAbsScaler,
        CatImputer,
        HashOneHotEncoder,
        LabelEncoder,
        CatTargetEncoder,
        WoETargetEncoder,
        OneHotEncoder,
        DateTimeTransformer,
        CountVectorizer,
        NaiveBayes,
        StringCast,
        TextTargetEncoder,
        TfIdf,
        WordEmbedding
    }


class PredictionTransformTypes:
    """Names for prediction transform types"""
    INTEGER = 'Integer'

    FULL_SET = {INTEGER}


class TransformerParams:
    """Defines parameters used by all transformers in AutoML."""

    class Imputer:
        """Defines how missing values are determined in imputer transformers in AutoML.

        The following example shows customizing featurization with the
        :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class
        and using one of the Imputer values.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.add_transformer_params('Imputer', ['columnName'], {"strategy": "median"})

        For more information, see `Configure automated ML experiments
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.
        """

        Strategy = "strategy"
        Constant = "constant"
        Mean = "mean"
        Median = "median"
        Mode = "most_frequent"
        Ffill = "ffill"
        FillValue = "fill_value"

        NumericalImputerStrategies = {Mean, Median}
        # Forecasting tasks specific parameters.
        ForecastingEnabledStrategies = {Mean, Median, Mode, Constant, Ffill}
        ForecastingTargetEnabledStrategies = {Constant, Ffill}

    class Nimbus:
        """Defines parameters used by nimbus in AutoML."""

        Mean = 'Mean'
        Min = 'Minimum'
        Max = 'Maximum'
        DefaultValue = 'DefaultValue'


class SupportedTransformersInternal(SupportedTransformers):
    """Defines transformer names for all transformers supported by AutoML, including those not exposed."""

    # Generic
    LambdaTransformer = 'LambdaTransformer'
    MiniBatchKMeans = 'MiniBatchKMeans'

    # Numeric
    BinTransformer = 'BinTransformer'

    # Text
    BagOfWordsTransformer = 'BagOfWordsTransformer'
    StringConcat = 'StringConcat'
    TextStats = 'TextStats'
    AveragedPerceptronTextTargetEncoder = 'AveragedPerceptronTextTargetEncoder'

    # TimeSeries
    GrainMarker = 'GrainMarker'
    MaxHorizonFeaturizer = 'MaxHorizonFeaturizer'
    Lag = 'Lag'
    RollingWindow = 'RollingWindow'
    STLFeaturizer = 'STLFeaturizer'
    TimeIndexFeaturizer = 'TimeIndexFeaturizer'

    # Ignore
    Drop = ''

    # For categorical indicator work column transformer
    DropColumnsTransformer = 'DropColumnsTransformer'

    FULL_SET = {
        LambdaTransformer,
        MiniBatchKMeans,
        BinTransformer,
        BagOfWordsTransformer,
        StringConcat,
        TextStats,
        AveragedPerceptronTextTargetEncoder,
        GrainMarker,
        MaxHorizonFeaturizer,
        Lag,
        RollingWindow,
        STLFeaturizer,
        TimeIndexFeaturizer,
        Drop
    }.union(set(SupportedTransformers.FULL_SET))


class SupportedTransformersFactoryNames:
    """Method names for transformers. These are Featurizer factory method names."""

    class Generic:
        """Supported transformer factory method for generic type data.

        For more information, see the :class:`azureml.automl.core.constants.SupportedTransformers` class.

        Attributes:
            ImputationMarker: Add boolean imputation marker for imputed values.

            LambdaTransformer: Transform data with a lambda function.

            Imputer: Complete missing values.

            MiniBatchKMeans: Transform data using Mini Batch K-Means.

            MaxAbsScaler: Scale data by its maximum absolute value.
        """

        ImputationMarker = 'imputation_marker'
        LambdaTransformer = 'lambda_featurizer'
        Imputer = 'imputer'
        MiniBatchKMeans = 'minibatchkmeans_featurizer'
        MaxAbsScaler = 'maxabsscaler'

    class Numeric:
        """Supported transformer factory method for numeric type data."""

        BinTransformer = 'bin_transformer'

    class Categorical:
        """Supported transformer factory method for categorical type data.

        For more information, see the :class:`azureml.automl.core.constants.SupportedTransformers` class.
        """

        CatImputer = 'cat_imputer'
        HashOneHotVectorizerTransformer = 'hashonehot_vectorizer'
        LabelEncoderTransformer = 'labelencoder'
        CatTargetEncoder = 'cat_targetencoder'
        WoEBasedTargetEncoder = 'woe_targetencoder'
        OneHotEncoderTransformer = 'onehotencoder'

    class DateTime:
        """Supported transformer factory method for datetime type data.

        For more information, see the :class:`azureml.automl.core.constants.SupportedTransformers` class.
        """

        DateTimeFeaturesTransformer = 'datetime_transformer'

    class Text:
        """Supported transformer factory method for text type data.

        For more information, see the :class:`azureml.automl.core.constants.SupportedTransformers` class.
        """
        BagOfWordsTransformer = 'bow_transformer'
        CountVectorizer = 'count_vectorizer'
        NaiveBayes = 'naive_bayes'
        StringCastTransformer = 'string_cast'
        StringConcatTransformer = 'string_concat'
        StatsTransformer = 'text_stats'
        TextTargetEncoder = 'text_target_encoder'
        AveragedPerceptronTextTargetEncoder = 'averaged_perceptron_text_target_encoder'
        TfidfVectorizer = 'tfidf_vectorizer'
        WordEmbeddingTransformer = 'word_embeddings'


class TransformerName:
    """Transformer names with customer and factory method names."""

    def __init__(self, customer_transformer_name, transformer_method_name):
        """Init TransformerName."""
        self.customer_transformer_name = customer_transformer_name
        self.transformer_method_name = transformer_method_name


class SupportedTransformerNames:
    """A list of supported transformers with all customer name and factory method name."""

    SupportedGenericTransformerList = [
        TransformerName(
            SupportedTransformersInternal.ImputationMarker,
            SupportedTransformersFactoryNames.Generic.ImputationMarker
        ),
        TransformerName(
            SupportedTransformersInternal.LambdaTransformer,
            SupportedTransformersFactoryNames.Generic.LambdaTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.Imputer,
            SupportedTransformersFactoryNames.Generic.Imputer
        ),
        TransformerName(
            SupportedTransformersInternal.MiniBatchKMeans,
            SupportedTransformersFactoryNames.Generic.MiniBatchKMeans
        ),
        TransformerName(
            SupportedTransformersInternal.MaxAbsScaler,
            SupportedTransformersFactoryNames.Generic.MaxAbsScaler
        ),
    ]

    SupportedNumericTransformerList = [
        TransformerName(
            SupportedTransformersInternal.BinTransformer,
            SupportedTransformersFactoryNames.Numeric.BinTransformer
        )
    ]

    SupportedCategoricalTransformerList = [
        TransformerName(
            SupportedTransformersInternal.CatImputer,
            SupportedTransformersFactoryNames.Categorical.CatImputer
        ),
        TransformerName(
            SupportedTransformersInternal.HashOneHotEncoder,
            SupportedTransformersFactoryNames.Categorical.HashOneHotVectorizerTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.LabelEncoder,
            SupportedTransformersFactoryNames.Categorical.LabelEncoderTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.CatTargetEncoder,
            SupportedTransformersFactoryNames.Categorical.CatTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.WoETargetEncoder,
            SupportedTransformersFactoryNames.Categorical.WoEBasedTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.OneHotEncoder,
            SupportedTransformersFactoryNames.Categorical.OneHotEncoderTransformer)
    ]

    SupportedDateTimeTransformerList = [
        TransformerName(
            SupportedTransformersInternal.DateTimeTransformer,
            SupportedTransformersFactoryNames.DateTime.DateTimeFeaturesTransformer
        )
    ]

    SupportedTextTransformerList = [
        TransformerName(
            SupportedTransformersInternal.BagOfWordsTransformer,
            SupportedTransformersFactoryNames.Text.BagOfWordsTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.CountVectorizer,
            SupportedTransformersFactoryNames.Text.CountVectorizer
        ),
        TransformerName(
            SupportedTransformersInternal.NaiveBayes,
            SupportedTransformersFactoryNames.Text.NaiveBayes
        ),
        TransformerName(
            SupportedTransformersInternal.StringCast,
            SupportedTransformersFactoryNames.Text.StringCastTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.StringConcat,
            SupportedTransformersFactoryNames.Text.StringConcatTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.TextStats,
            SupportedTransformersFactoryNames.Text.StatsTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.TextTargetEncoder,
            SupportedTransformersFactoryNames.Text.TextTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.TfIdf,
            SupportedTransformersFactoryNames.Text.TfidfVectorizer
        ),
        TransformerName(
            SupportedTransformersInternal.AveragedPerceptronTextTargetEncoder,
            SupportedTransformersFactoryNames.Text.AveragedPerceptronTextTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.WordEmbedding,
            SupportedTransformersFactoryNames.Text.WordEmbeddingTransformer
        )
    ]


class TransformerNameMappings:
    """Transformer name mappings."""

    CustomerFacingTransformerToTransformerMapGenericType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedGenericTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedGenericTransformerList]))

    CustomerFacingTransformerToTransformerMapCategoricalType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedCategoricalTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedCategoricalTransformerList]))

    CustomerFacingTransformerToTransformerMapNumericType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedNumericTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedNumericTransformerList]))

    CustomerFacingTransformerToTransformerMapDateTimeType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedDateTimeTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedDateTimeTransformerList]))

    CustomerFacingTransformerToTransformerMapText = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedTextTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedTextTransformerList]))


class TextNeuralNetworks:
    """Names of neural models swept for text classification."""

    # feature sweeping config names
    BILSTM = "BiLSTMTextEmbeddings"
    BERT = "PreTrainedDNNEmbeddings"
    ALL = [BILSTM, BERT]

    # class names
    BILSTM_CLASS_NAME = "BiLSTMAttentionTransformer"
    BERT_CLASS_NAME = "PretrainedTextDNNTransformer"
    ALL_CLASS_NAMES = [BILSTM_CLASS_NAME, BERT_CLASS_NAME]


class _OperatorNames:
    """Class storing operator names for various transformations."""

    CharGram = 'CharGram'
    WordGram = 'WordGram'
    Mean = 'Mean'
    Mode = 'Mode'
    Median = 'Median'
    Constant = 'Constant'
    ForwardFill = 'FowardFill'
    Min = 'Min'
    Max = 'Max'
    DefaultValue = 'DefaultValue'

    FULL_SET = {CharGram, WordGram, Mean, Mode, Median, Min, Max, Constant, DefaultValue}


class _TransformerOperatorMappings:
    Imputer = {
        TransformerParams.Imputer.Mean: _OperatorNames.Mean,
        TransformerParams.Imputer.Mode: _OperatorNames.Mode,
        TransformerParams.Imputer.Median: _OperatorNames.Median,
        TransformerParams.Imputer.Constant: _OperatorNames.Constant,
        TransformerParams.Imputer.Ffill: _OperatorNames.ForwardFill
    }
    NimbusImputer = {
        TransformerParams.Nimbus.Mean: _OperatorNames.Mean,
        TransformerParams.Nimbus.Min: _OperatorNames.Min,
        TransformerParams.Nimbus.Max: _OperatorNames.Max,
        TransformerParams.Nimbus.DefaultValue: _OperatorNames.DefaultValue
    }


class SweepingMode:
    """Defines mode names for feature and class balancing sweeping."""

    Feature = 'feature'
    Balancing = 'balancing'


class LanguageUnicodeRanges:
    """ Class storing nons-spaced languages' unicode ranges. Chinese is an example of a non-spaced language."""
    nonspaced_language_unicode_ranges = [
        (0x4E00, 0x9FFF), (0x3400, 0x4DBF),                   # Japanese and Chinese shared
        (0x300, 0x30FF), (0xFF00, 0xFFEF),                    # Japanese
        (0x20000, 0x2A6DF), (0x2A700, 0x2B73F),               # Chinese
        (0x2B740, 0x2B81F), (0x2B820, 0x2CEAF),
        (0xF900, 0xFAFF), (0x2F800, 0x2FA1F),
        (0x1000, 0x109F), (0xAA60, 0XAA7F), (0xA9E0, 0xA9FF)  # Burmese
    ]


class TextDNNLanguages:
    """Class storing supported text dnn languages."""
    default = "eng"
    cpu_supported = {"eng": "English"}
    supported = {
        "afr": "Afrikaans",
        "ara": "Arabic",
        "arg": "Aragonese",
        "ast": "Asturian",
        "azb": "South Azerbaijani",
        "aze": "Azerbaijani",
        "bak": "Bashkir",
        "bar": "Bavarian",
        "bel": "Belarusian",
        "ben": "Bengali",
        "bos": "Bosnian",
        "bpy": "Bishnupriya",
        "bre": "Breton",
        "bul": "Bulgarian",
        "cat": "Catalan",
        "ceb": "Cebuano",
        "ces": "Czech",
        "che": "Chechen",
        "chv": "Chuvash",
        "cym": "Welsh",
        "dan": "Danish",
        "deu": "German",
        "ell": "Greek",
        "eng": "English",
        "est": "Estonian",
        "eus": "Basque",
        "fas": "Persian",
        "fin": "Finnish",
        "fra": "French",
        "fry": "Western Frisian",
        "gle": "Irish",
        "glg": "Galician",
        "guj": "Gujarati",
        "hat": "Haitian",
        "hbs": "Serbo-Croatian",
        "heb": "Hebrew",
        "hin": "Hindi",
        "hrv": "Croatian",
        "hun": "Hungarian",
        "hye": "Armenian",
        "ido": "Ido",
        "ind": "Indonesian",
        "isl": "Icelandic",
        "ita": "Italian",
        "jav": "Javanese",
        "jpn": "Japanese",
        "kan": "Kannada",
        "kat": "Georgian",
        "kaz": "Kazakh",
        "kir": "Kirghiz",
        "kor": "Korean",
        "lah": "Western Punjabi",
        "lat": "Latin",
        "lav": "Latvian",
        "lit": "Lithuanian",
        "lmo": "Lombard",
        "ltz": "Luxembourgish",
        "mal": "Malayalam",
        "mar": "Marathi",
        "min": "Minangkabau",
        "mkd": "Macedonian",
        "mlg": "Malagasy",
        "mon": "Mongolian",
        "msa": "Malay",
        "mul": "Multilingual - collection of all supporting languages",
        "mya": "Burmese",
        "nds": "Low Saxon",
        "nep": "Nepali",
        "new": "Newar",
        "nld": "Dutch",
        "nno": "Norwegian Nynorsk",
        "nob": "Norwegian Bokmål",
        "oci": "Occitan",
        "pan": "Punjabi",
        "pms": "Piedmontese",
        "pol": "Polish",
        "por": "Portuguese",
        "ron": "Romanian",
        "rus": "Russian",
        "scn": "Sicilian",
        "sco": "Scots",
        "slk": "Slovak",
        "slv": "Slovenian",
        "spa": "Spanish",
        "sqi": "Albanian",
        "srp": "Serbian",
        "sun": "Sundanese",
        "swa": "Swahili",
        "swe": "Swedish",
        "tam": "Tamil",
        "tat": "Tatar",
        "tel": "Telugu",
        "tgk": "Tajik",
        "tgl": "Tagalog",
        "tha": "Thai",
        "tur": "Turkish",
        "ukr": "Ukrainian",
        "urd": "Urdu",
        "uzb": "Uzbek",
        "vie": "Vietnamese",
        "vol": "Volapük",
        "war": "Waray-Waray",
        "yor": "Yoruba",
        "zho": "Chinese"
    }


class RunHistoryEnvironmentVariableNames:
    """Constants for Run History environment variable names."""

    AZUREML_ARM_SUBSCRIPTION = "AZUREML_ARM_SUBSCRIPTION"
    AZUREML_RUN_ID = "AZUREML_RUN_ID"
    AZUREML_ARM_RESOURCEGROUP = "AZUREML_ARM_RESOURCEGROUP"
    AZUREML_ARM_WORKSPACE_NAME = "AZUREML_ARM_WORKSPACE_NAME"
    AZUREML_ARM_PROJECT_NAME = "AZUREML_ARM_PROJECT_NAME"
    AZUREML_EXPERIMENT_ID = 'AZUREML_EXPERIMENT_ID'
    AZUREML_RUN_TOKEN = "AZUREML_RUN_TOKEN"
    AZUREML_SERVICE_ENDPOINT = "AZUREML_SERVICE_ENDPOINT"
    AZUREML_DISCOVERY_SERVICE_ENDPOINT = "AZUREML_DISCOVERY_SERVICE_ENDPOINT"
    AZUREML_AUTOML_RUN_HISTORY_DATA_PATH = "AZUREML_AUTOML_RUN_HISTORY_DATA_PATH"


class PreparationRunTypeConstants:
    """
    Constants for specifying what sort of prep run (e.g. setup only, setup before
    featurization, featurization only) we're doing before model selection.
    """
    SETUP_WITHOUT_FEATURIZATION = "setup_without_featurization"
    SETUP_ONLY = "setup_only"
    FEATURIZATION_ONLY = "featurization_only"


class FeaturizationRunConstants:
    """
    Constants relevant to the generation of the featurization run, along with
    default paths for artifacts to be transferred from the setup run.
    """
    CONFIG_PATH = "feature_config.pkl"
    CONFIG_PROP = "ChosenFeaturizersPath"

    FEATURIZATION_JSON_PATH = "featurizer_container.json"
    FEATURIZATION_JSON_PROP = "FeaturizationRunJsonPath"

    # will likely be removed after logic relating to
    # _GeneratedEngineeredFeatureNames is sorted out
    NAMES_PATH = "feature_names.pkl"
    NAMES_PROP = "EngineeredNamesPath"

    FEATURIZER_CACHE_PREFIX = "Featurizer_"

    # JSON keys
    FEATURIZERS_KEY = "featurizers"
    INDEX_KEY = "index"
    TRANSFORMERS_KEY = "transformers"
    CACHED = "is_cached"
    IS_DISTRIBUTABLE = "is_distributable"
    IS_SEPARABLE = "is_separable"


FEATURIZERS_NOT_TO_BE_SHOWN_IN_ENGG_FEAT_NAMES = {
    SupportedTransformersInternal.StringCast, SupportedTransformersInternal.DateTimeTransformer
}


class HTSConstants:
    HIERARCHY = "hierarchy_column_names"
    HTS_INPUT = "hts_raw"
    TRAINING_LEVEL = "hierarchy_training_level"

    # Column names related constants
    HTS_CROSS_TIME_PROPORTION = "_hts_cross_time_proportion"
    HTS_CROSS_TIME_SUM = "_hts_cross_time_sum"
    HTS_ENDTIME = "_hts_endtime"
    HTS_FREQUENCY = "_hts_freq"
    HTS_HIERARCHY_SUM = "_hts_hierarchy_sum"
    HTS_STARTTIME = "_hts_starttime"
    PREDICTION_COLUMN = "automl_predictions"

    # Graph related constants
    NODE_ID = "node_id"
    HTS_ROOT_NODE_NAME = "AutoML_HTS_ROOT"
    HTS_ROOT_NODE_LEVEL = "_ROOT_LEVEL"

    # Logging related constants
    LOGGING_PIPELINE_ID = "pipeline_run_id"
    LOGGING_RUN_ID = "script_run_id"
    LOGGING_RUN_TYPE = "run_type"
    LOGGING_SCRIPT_SESSION_ID = "script_session_id"

    # script arguments constants
    ALLOCATION_METHOD = "--allocation-method"
    BLOB_PATH = "--filedataset-blob-dir"
    ENABLE_EVENT_LOGGER = "--enable-event-logger"
    FORECAST_LEVEL = "--forecast-level"
    METADATA_INPUT = "--input-medatadata"
    OUTPUT_PATH = "--output-path"
    RAW_FORECASTS = "--raw-forecasts"
    TRAINING_RUN_ID = "--training-runid"

    # json fields constants
    AVERAGE_HISTORICAL_PROPORTIONS = "average_historical_proportions"
    COLLECT_SUMMARY_JSON_AGG_FILE = "aggregated_file"
    COLLECT_SUMMARY_JSON_ORIGIN_FILE = "origin_files"
    COLLECT_SUMMARY_JSON_SUMMARY = "summary"
    PROPORTIONS_OF_HISTORICAL_AVERAGE = "proportions_of_historical_average"
    RUN_INFO_STATUS = "status"
    COLUMN_VOCABULARY_DICT = "column_vocabulary_dict"
    RUN_INFO_AUTOML_RUN_ID = "run_id"
    RUN_INFO_FAILED_REASON = "failed_reason"

    # run properties and model tags constants
    MODEL_TAG_AUTOML = "AutoML"
    MODEL_TAG_MODEL_TYPE = "ModelType"
    MODEL_TAG_STEP_RUN_ID = "StepRunId"
    MODEL_TAG_RUN_ID = "RunId"
    MODEL_TAG_HIERARCHY = "Hierarchy"
    MODEL_TAG_HASH = "HASH"
    RUN_PROPERTIES_MANY_MODELS_RUN = "many_models_run"
    RUN_PROPERTIES_INPUT_FILE = "many_models_input_file"
    RUN_PROPERTIES_DATA_TAGS = "many_models_data_tags"
    METADATA_JSON_METADATA = "metadata"
    JSON_VERSION = "version"

    # hts steps realated constants
    STEP_PRE_PROPORTIONS_CALCULATION = "pre-proportions-calculation"
    STEP_DATA_AGGREGATION = "data-aggregation-and-validation"
    STEP_DATA_AGGREGATION_FILEDATASET = "data-aggregation-filedataset"
    STEP_AUTOML_TRAINING = "automl-training"
    STEP_PROPORTIONS_CALCULATION = "proportions-calculation"
    STEP_FORECAST = "forecast-parallel"
    STEP_ALLOCATION = "forecast-allocation"

    # File related constants
    GRAPH_JSON_FILE = "hts_graph.json"
    HTS_CROSS_TIME_AGG_CSV = "hts_cross_time_agg.csv"
    HTS_FILE_COLUMN_VOCABULARY_JSON = "column_vocabulary.json"
    HTS_FILE_DATASET_COLLECT_SUMMARY = "dataset_collect_summary.json"
    HTS_FILE_POSTFIX_COLUMN_VOCABULARY_JSON = "_column_vocabulary.json"
    HTS_FILE_POSTFIX_METADATA_CSV = "_metadata.csv"
    HTS_FILE_POSTFIX_RUN_INFO_JSON = "_run_info.json"
    HTS_FILE_PRED_RESULTS_POSTFIX = "_results.json"
    HTS_FILE_PRED_RESULTS = "prediction_results.json"
    HTS_FILE_PREDICTIONS = "allocated_predictions.csv"
    HTS_FILE_PREDICTIONS_POSTFIX = "_pred.csv"
    HTS_FILE_PROPORTIONS_METADATA_JSON = "metadata.json"
    HTS_FILE_RUN_INFO_JSON = "run_info.json"
    SETTINGS_FILE = "automl_settings.json"

    # tuning parameters constants.
    HTS_COUNT_VECTORIZER_MAX_FEATURES = 5

    AGGREGATION_METHODS = {AVERAGE_HISTORICAL_PROPORTIONS, PROPORTIONS_OF_HISTORICAL_AVERAGE}

    HIERARCHY_PARAMETERS = {HIERARCHY, TRAINING_LEVEL}

    HTS_SCRIPTS_SCENARIO_ARG_DICT = {
        STEP_PRE_PROPORTIONS_CALCULATION: [OUTPUT_PATH, BLOB_PATH, ENABLE_EVENT_LOGGER],
        STEP_DATA_AGGREGATION: [OUTPUT_PATH, BLOB_PATH, METADATA_INPUT, ENABLE_EVENT_LOGGER],
        STEP_AUTOML_TRAINING: [OUTPUT_PATH, METADATA_INPUT, ENABLE_EVENT_LOGGER],
        STEP_PROPORTIONS_CALCULATION: [METADATA_INPUT, ENABLE_EVENT_LOGGER],
        STEP_FORECAST: [TRAINING_RUN_ID, OUTPUT_PATH, ENABLE_EVENT_LOGGER],
        STEP_ALLOCATION: [
            FORECAST_LEVEL, ALLOCATION_METHOD, TRAINING_RUN_ID, OUTPUT_PATH, RAW_FORECASTS, ENABLE_EVENT_LOGGER]
    }

    HTS_OUTPUT_ARGUMENTS_DICT = {
        ENABLE_EVENT_LOGGER: "enable_event_logger",
        OUTPUT_PATH: "output_path",
        METADATA_INPUT: "input_metadata",
        FORECAST_LEVEL: "forecast_level",
        ALLOCATION_METHOD: "allocation_method",
        TRAINING_RUN_ID: "training_run_id",
        RAW_FORECASTS: "raw_forecasts",
        OUTPUT_PATH: "output_path",
        METADATA_INPUT: "input_metadata",
        BLOB_PATH: 'filedataset_blob_dir'
    }
