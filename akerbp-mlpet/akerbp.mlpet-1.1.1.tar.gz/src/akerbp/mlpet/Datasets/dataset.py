import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml
from pandas.core.frame import DataFrame

from akerbp.mlpet.Datasets import (
    feature_engineering,
    imputers,
    preprocessors,
    utilities,
)
from akerbp.mlpet.Datasets.dataloader import DataLoader


class Dataset(DataLoader):
    """
    The main class representing a dataset

    Note:
        **All settings keys are set as class attributes**

    Args:
        mappings: dict or path to a yaml file. If a path is provided it must
            either be provided as an absolute path or relative path to the mlpet
            package (folder).
        settings: dict or path to a yaml file. If a path is provided it must
            either be provided as an absolute path or relative path to the mlpet
            package (folder). The possible keys for the settings:

                - data_path (required): pickled filename (the full path or relative path from the mlpet package) to read the data from, or dump the data to,
                - curves (required): list of features from the raw data to use,
                - id_column (required): name of the id column, eg. well_name
                - label_column (optional): name of the column containing the labels
                - curves_to_scale (optional - default []): list of curves from the curves list should be scaled,
                - curves_to_normalize (optional - default []): list of curves from the curves list should be 2-point normalized
                - num_filler (optional - default 0): filler value for numerical curves(existing or wishing value for replacing missing values)
                - cat_filler (optional - default 'MISSING'): filler value categorical curves(existing or wishing value for replacing missing values)
                - scaler_method (optional - default 'RobustScaler'): (options: 'StandardScaler', 'RobustScaler', 'MinMaxScaler')
                - log_features (optional - default []): list of curves to calculate the base 10 log of
                - gradient_features (optional - default []): list of curves to calculate gradients features for
                - rolling_features (optional - default []): list of curves to calculate rolling window aggregations (min, max, mean) of
                - window (optional - default 1): size of the rolling window for calculating the window features (int)
                - sequential_features (optional - default []): list of curves to calculate sequential features for (shifted features)
                - petrophysical_features (optional - default []): list of petrophysical curves to create. See add_petrophysical_features in feature_engineering modue for which ones are available
                - noise_removal_window (optional - default None): int, if a median filtering of each curve is required. if None no filtering is applied
                - imputer (optional - default None): 'iterative' for IterativeImputer or 'simple' for SimpleImputer
                - categorical_curves (optional - default []): list of curves which should be considered as categorical. If none is specified the algorithm tries to determine the categorical columns

        folder_path: The path to where preprocessing artifacts are stored/shall
            be saved to. Similar to the other two arguments this path must be
            provided as an absolute path or relative path to the mlpet package
            (folder).

    """

    # Setting type annotations for class attributes that are set when an
    # instances of the Dataset class is created
    settings: Dict[str, Any]
    settings_path: str
    curves: List[str]
    curves_to_normalize: List[str]
    curves_to_scale: List[str]
    data_path: Union[str, Path]
    id_column: str
    label_column: str
    log_features: List[str]
    num_filler: float
    rolling_features: List[str]
    gradient_features: List[str]
    sequential_features: List[str]
    mappings: Dict[str, Any]
    categorical_curves: List[str]
    petrophysical_features: List[str]
    scaler_method: str
    window: int

    def __handle_paths(self, path: Union[Path, str]) -> Union[Path, str]:
        this_dir = Path(__file__).parent
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(this_dir, "..", path))
        return path

    def __set_defaults(self) -> None:
        if not hasattr(self, "curves_to_scale"):
            self.curves_to_scale = []

        if not hasattr(self, "scaler_method"):
            self.scaler_method = "RobustScaler"

        if not hasattr(self, "categorical_curves"):
            self.categorical_curves = []

        if not hasattr(self, "log_features"):
            self.log_features = []

        if not hasattr(self, "gradient_features"):
            self.gradient_features = []

        if not hasattr(self, "rolling_features"):
            self.rolling_features = []

        if not hasattr(self, "window"):
            self.window = 1

        if not hasattr(self, "sequential_features"):
            self.sequential_features = []

        if not hasattr(self, "noise_removal_window"):
            self.noise_removal_window = None

        if not hasattr(self, "petrophysical_features"):
            self.petrophysical_features = []

        if not hasattr(self, "num_filler"):
            self.num_filler = 0

        if not hasattr(self, "cat_filler"):
            self.cat_filler = "MISSING"

        if not hasattr(self, "include_depth_label"):
            self.include_depth_label = False

        if not hasattr(self, "curves_to_normalize"):
            warnings.warn(
                '"curves_to_normalize" not provided in dataset settings. Note that you are NOT normalizing "GR", make sure this is intentional!'
            )
            self.curves_to_normalize = []

        if not hasattr(self, "imputer"):
            self.imputer = None

    def __init__(
        self,
        mappings: Union[str, Dict[str, str]],
        settings: Union[str, Dict[str, Any]],
        folder_path: Union[str, Path],
    ) -> None:
        def ingest_input(
            att_name: str, att_val: Union[str, Dict[str, Any], Path]
        ) -> None:
            if isinstance(att_val, dict):
                setattr(self, att_name, att_val)
            elif isinstance(att_val, str):
                att_val = self.__handle_paths(att_val)
                if os.path.isfile(att_val):
                    att_path = f"{att_name}_path"
                    setattr(self, att_path, att_val)
                    with open(getattr(self, att_path)) as file:
                        setattr(self, att_name, yaml.load(file, Loader=yaml.SafeLoader))
                else:
                    raise FileNotFoundError(
                        f"The provided filepath {att_val} is not a valid path! "
                        f"The Dataset cannot be initialised without a {att_name}.yaml!"
                        " Please refer to the classes' docstring to ensure you have"
                        " specified your filepath in the correct form."
                    )

        self.folder_path = self.__handle_paths(folder_path)
        if not os.path.isdir(self.folder_path):
            os.makedirs(self.folder_path)

        ingest_input(att_name="settings", att_val=settings)
        for key, val in self.settings.items():
            setattr(self, key, val)

        ingest_input(att_name="mappings", att_val=mappings)
        if "curve_mappings" in self.mappings:
            self.curve_mappings = self.mappings["curve_mappings"]
        if "formations_map" in self.mappings:
            self.formations_map = self.mappings["formations_map"]
        if "groups_map" in self.mappings:
            self.groups_map = self.mappings["groups_map"]

        # Fill in any possible gaps in settings with defaults
        self.__set_defaults()

        # Standardize the provided curve names
        original_curve_names = {}
        for attr in [
            "curves",
            "curves_to_scale",
            "curves_to_normalize",
            "rolling_features",
            "gradient_features",
            "log_features",
            "sequential_features",
            "categorical_curves",
        ]:
            setattr(self, f"{attr}_original", getattr(self, attr))
            new_names, original_curve_names[attr] = utilities.standardize_names(
                names=getattr(self, attr), mapper=self.curve_mappings
            )
            setattr(self, attr, new_names)

        # standardize label columns
        tmp_label_column, original_label_col = utilities.standardize_names(
            [self.label_column], mapper=self.curve_mappings
        )
        self.label_column = tmp_label_column[0]
        # Check that the label curve is not present in the curves
        if self.label_column in self.curves:
            original_col_label = original_label_col[self.label_column]
            original_col_curve = original_curve_names["curves"][self.label_column]
            raise ValueError(
                f"Label column ({original_col_label}) is present in the input curves ({original_col_curve})."
            )

        # Check that all curves, required to accomplish the preprocessing steps
        # requested, are provided
        all_curves = set(self.curves)
        for attr in [
            "curves_to_scale",
            "curves_to_normalize",
            "rolling_features",
            "gradient_features",
            "log_features",
            "sequential_features",
            "categorical_curves",
        ]:
            sub_curves = set(getattr(self, attr))
            if not sub_curves.issubset(all_curves):
                sub_curves = set([original_curve_names[attr][c] for c in sub_curves])
                all_curves = set(
                    [original_curve_names["curves"][c] for c in all_curves]
                )
                raise ValueError(f"{sub_curves} is not a subset of curves {all_curves}")

        # Check that categorical curves includes the id_column (to prevent
        # unnesscery warnings later on)
        if self.id_column and self.categorical_curves:
            self.categorical_curves = list(
                set(self.categorical_curves + [self.id_column])
            )

        try:
            self.data_path = self.__handle_paths(self.data_path)
        except AttributeError as ae:
            raise AttributeError(
                "No data_path was set in your settings file! This setting is "
                "required. Please refer to the docstring."
            ) from ae

        # Define supported preprocessing functions
        self.supported_preprocessing_functions = {
            f.__name__: f
            for f in [
                feature_engineering.add_log_features,
                feature_engineering.add_gradient_features,
                feature_engineering.add_rolling_features,
                feature_engineering.add_sequential_features,
                feature_engineering.add_formation_tops_label,
                feature_engineering.add_petrophysical_features,
                imputers.impute_depth_trend,
                imputers.iterative_impute,
                imputers.simple_impute,
                preprocessors.set_as_nan,
                preprocessors.remove_outliers,
                preprocessors.remove_small_negative_values,
                preprocessors.fill_zloc_from_depth,
                preprocessors.fillna_with_fillers,
                preprocessors.encode_columns,
                preprocessors.select_curves,
                preprocessors.normalize_curves,
                preprocessors.scale_curves,
                preprocessors.process_wells,
                preprocessors.remove_noise,
            ]
        }

        # Define default preprocessing workflow to use if none is provided at runtime
        self.default_preprocessing_workflow = [
            "set_as_nan",
            "remove_outliers",
            "impute_depth_trend",
            "remove_noise",
            "add_petrophysical_features",
            "normalize_curves",
            "add_log_features",
            "process_wells",
            "fill_zloc_from_depth",
            "fillna_with_fillers",
            "encode_columns",
            "scale_curves",
        ]

    def preprocess(self, df: DataFrame = None, **kwargs) -> DataFrame:
        """
        Main preprocessing function. Pass the dataframe to be preprocessed along
        with any kwargs for running any desired order (within reason) of the
        various supported preprocessing functions.

        To see which functions are supported for preprocessing you can access
        the class attribute 'supported_preprocessing_functions'.

        To see what all the default settings are for all the supported preprocessing
        functions are, run the class 'get_preprocess_defaults' method without any
        arguments.

        To see what kwargs are being used for the default workflow, run the
        class 'get_preprocess_defaults' with the class attribute
        'default_preprocessing_workflow' as the main arg.

        Warning:
            The preprocess function will run through the provided kwargs in the
            order provided by the kwargs dictionary. In python 3.7+, dictionaries
            are insertion ordered and it is this implemnetational detail this function
            builds upon. As such, do not use any Python version below 3.7 or ensure
            to pass an OrderedDict instance as your kwargs to have complete control
            over what order the preprocessing functions are run in!

        Args:
            df (pd.Dataframe, optional): dataframe to which apply preprocessing.
                If none is provided, it will use the class' original df if exists.

        Keyword Args:
            See above in the docstring on all potential kwargs and their relevant
            structures.

        Returns:
            pd.Dataframe: preprocessed dataframe
        """
        # <---------------- Perform admin/prep work -------------------------> #
        # If no dataframe is provided, use class df_original
        if df is None:
            if hasattr(self, "df_original"):
                df = self.df_original
                if df.empty:
                    raise ValueError(
                        "The class connected pd.Dataframe ('df_original') has "
                        "no data so there is nothing to preprocess!"
                    )
            else:
                raise ValueError(
                    "This Dataset class instance does not have a pd.DataFrame "
                    "attached to it so there is no data to preprocess!"
                )

        # Keep track of original column names
        original_columns = set(df.columns)

        # Validate data first
        self.validate_data()

        # Standardize curve names
        df = utilities.standardize_curve_names(df, mapper=self.curve_mappings)

        # <---------------- Perform preprocessing pipeline ------------------> #
        # Define kwargs to be used in preprocess method calls
        if not kwargs:
            # User did not provide any kwargs so running default workflow
            kwargs = {f: {} for f in self.default_preprocessing_workflow}
        kwargs = self.get_preprocess_defaults(kwargs)

        # Perform preprocessing pipeline
        for function, settings in kwargs.items():
            df = self.supported_preprocessing_functions[function](df, **settings)

        # Perform admin work on detecting features created and removed
        self.features_added = list(
            set([x for x in df.columns if x not in original_columns])
        )
        self.original_columns_removed = list(
            set([x for x in original_columns if x not in df.columns])
        )

        return df

    def get_preprocess_defaults(
        self, kwargs: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wrapper function to define and provide the default kwargs to use for
        preprocessing. This function allows the user to only tweak certain
        function kwargs rather than having to define a setting for every single
        function kwargs. If a kwargs dictionary is passed to the function, only
        the defaults for the provided function names found in the kwargs will be
        returned. In other words, to generate a full default kwargs example, run
        this method without any arguments.

        Args:
            kwargs (Dict[str, Any], optional): Any user defined kwargs that should
                override the defaults. Defaults to {}.

        Returns:
            Dict[str, Any]: A populated kwargs dictionary to be passed to all
                supported methods in preprocessing.
        """
        # Define per method defaults
        defaults: Dict[str, Dict[str, Any]] = {
            "add_log_features": {"log_features": self.log_features},
            "add_gradient_features": {"gradient_features": self.gradient_features},
            "add_rolling_features": {
                "rolling_features": self.rolling_features,
                "window": self.window,
            },
            "add_sequential_features": {
                "sequential_features": self.sequential_features,
                "n": 5,
            },
            "add_formation_tops_label": {
                "id_column": self.id_column,
            },
            "add_petrophysical_features": {
                "petrophysical_features": self.petrophysical_features,
                "id_column": self.id_column,
            },
            "simple_impute": {"categorical_curves": self.categorical_curves},
            "iterative_impute": {"imputer": None},
            "impute_depth_trend": {
                "curves_to_impute": None,
                "imputation_models": None,
                "save_imputation_models": False,
                "allow_individual_models": True,
                "folder_path": self.folder_path,
                "curves_mapping": self.curve_mappings,
            },
            "set_as_nan": {
                "numerical_value": -999,
                "categorical_value": "MISSING",
                "categorical_column_names": self.categorical_curves,
            },
            "remove_outliers": {"curves": self.curves, "threshold": 0.05},
            "remove_small_negative_values": {"nan_threshold": -999},
            "fill_zloc_from_depth": {},
            "fillna_with_fillers": {
                "num_filler": self.num_filler,
                "cat_filler": self.cat_filler,
                "categorical_columns": self.categorical_curves,
            },
            "encode_columns": {
                "columns": self.categorical_curves,
                "formations_map": self.formations_map,
                "groups_map": self.groups_map,
                "missing_encoding_value": -1,
            },
            "select_curves": {
                "curves": self.curves,
                "label_column": self.label_column,
                "id_column": self.id_column,
            },
            "normalize_curves": {
                "low_perc": 0.05,
                "high_perc": 0.95,
                "save_key_wells": False,
                "curves_to_normalize": self.curves_to_normalize,
                "id_column": self.id_column,
                "user_key_wells": {},
                "folder_path": self.folder_path,
            },
            "scale_curves": {
                "scaler_method": self.scaler_method,
                "scaler": None,
                "save_scaler": False,
                "folder_path": self.folder_path,
                "curves_to_scale": self.curves_to_scale,
                "scaler_kwargs": {},
            },
            "process_wells": {
                "id_column": self.id_column,
                "imputation_type": self.imputer,
            },
            "remove_noise": {
                "curves": [],  # Default behaviour is to apply to all numeric cols
                "noise_removal_window": self.noise_removal_window,
            },
        }

        # Process wells uses a bunch of lower level functions so we need to
        # enrich it's kwargs with the relevant kwargs
        methods_used_by_process_wells = [
            "simple_impute",
            "iterative_impute",
            "add_rolling_features",
            "add_gradient_features",
            "add_sequential_features",
        ]
        for method in methods_used_by_process_wells:
            defaults["process_wells"].update(defaults[method])

        # Ingest defaults into kwargs if they exist
        if kwargs is not None:
            for function_name in kwargs:
                # retrieve default settings for function
                default_function_settings = defaults[function_name]
                # Populate kwargs with all non provided defaults
                for setting_name, default_setting in default_function_settings.items():
                    set_result = kwargs[function_name].setdefault(
                        setting_name, default_setting
                    )
                    # Need to perform some more advanced operations for specifically mapping
                    # dictionaries
                    # First, if the setting is of type dict (e.g. a mapping dict)
                    # need to ensure that we preserve the users mapping and combine
                    # them with any existing mappings created for example upon
                    # class initilisation.
                    if isinstance(set_result, dict) and set_result != default_setting:
                        if setting_name in [
                            "formations_map",
                            "groups_map",
                            "curves_mapping",
                        ]:  # Append/Overwrite user provided mappings to existing mappings
                            kwargs[function_name][setting_name] = {
                                **default_setting,
                                **set_result,
                            }

            return kwargs

        return defaults

    def validate_data(self) -> None:
        """
        Checks that the data loaded into the Dataset includes the expected curves
        """
        # standardize curve names
        df_original = utilities.standardize_curve_names(
            self.df_original, mapper=self.curve_mappings
        )
        # check that all expected curves are present in the data
        expected_curves = self.curves
        present_curves = df_original.columns.tolist()
        expected_but_missing_curves = [
            c for c in expected_curves if c not in present_curves
        ]
        if expected_but_missing_curves:
            expected_but_missing_cat_curves = set(expected_but_missing_curves) & set(
                self.categorical_curves
            )
            expected_but_missing_num_curves = (
                set(expected_but_missing_curves) - expected_but_missing_cat_curves
            )
            warnings.warn(
                "There are curves that are expected but missing from data. "
                "These curves are being filled with cat_filler:  "
                f"{expected_but_missing_cat_curves}"
                "\nThese curves are being filled with num_filler: "
                f"{expected_but_missing_num_curves}"
            )
            df_original[list(expected_but_missing_cat_curves)] = self.cat_filler
            df_original[list(expected_but_missing_num_curves)] = self.num_filler
