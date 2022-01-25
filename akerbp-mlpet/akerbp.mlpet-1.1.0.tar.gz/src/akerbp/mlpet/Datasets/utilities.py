import re
import warnings
from typing import Any, Dict, List, Set, Tuple, Union

import numpy as np
import pandas as pd
from cognite.client import CogniteClient
from cognite.client.data_classes import Asset, AssetList
from numpy import float64


def drop_rows_wo_label(df: pd.DataFrame, label_column: str, **kwargs) -> pd.DataFrame:
    """
    Removes columns with missing targets.

    Now that the imputation is done via pd.df.fillna(), what we need is the constant filler_value
    If the imputation is everdone using one of sklearn.impute methods or a similar API, we can use
    the indicator column (add_indicator=True)

    Args:
        df (pd.DataFrame): dataframe to process
        label_column (str): Name of the label column containing rows without labels

    Keyword Args:
        missing_label_value (str, optional): If nans are denoted differently than np.nans,
            a missing_label_value can be passed as a kwarg and all rows containing
            this missing_label_value in the label column will be dropped


    Returns:
        pd.DataFrame: processed dataframe
    """
    missing_label_value = kwargs.get("missing_label_value")
    if missing_label_value is not None:
        return df.loc[df[label_column] != missing_label_value, :]
    else:
        return df.loc[~df[label_column].isna(), :]


def standardize_group_formation_name(name: str) -> str:
    """
    Performs several string operations to standardize group formation names
    for later categorisation.

    Args:
        name (str): A group formation name

    Returns:
        str: Returns the standardized group formation name.
    """
    if "INTRA" in name or "NO " in name:
        name = " ".join(name.split(" ")[:2])
        name = " ".join(name.split("_")[:2])
    else:
        name = name.split(" ")[0]
        name = name.split("_")[0]
        name = name.upper()
        name = name.replace("AA", "A")
        name = name.replace("Å", "A")
        name = name.replace("AE", "A")
        name = name.replace("Æ", "A")
        name = name.replace("OE", "O")
        name = name.replace("Ø", "O")
    return name


def standardize_names(
    names: List[str], mapper: Dict[str, str]
) -> Tuple[List[str], Dict[str, str]]:
    """
    Standardize curve names in a list based on the curve_mappings dictionary.
    Any columns not in the dictionary are ignored.

    Args:
        names (list): list with curves names
        mapper (dictionary): dictionary with mappings. Defaults to curve_mappings.

    Returns:
        list: list of strings with standardized curve names
    """
    standardized_names = []
    for name in names:
        mapped_name = mapper.get(name)
        if mapped_name:
            standardized_names.append(mapped_name)
        else:
            standardized_names.append(name)
    old_new_cols = {n: o for o, n in zip(names, standardized_names)}
    return standardized_names, old_new_cols


def standardize_curve_names(df: pd.DataFrame, mapper: Dict[str, str]) -> pd.DataFrame:
    """
    Standardize curve names in a dataframe based on the curve_mappings dictionary.
    Any columns not in the dictionary are ignored.

    Args:
        df (pd.DataFrame): dataframe to which apply standardization of columns names
        mapper (dictionary): dictionary with mappings. Defaults to curve_mappings.
            They keys should be the old curve name and the values the desired
            curved name.

    Returns:
        pd.DataFrame: dataframe with columns names standardized
    """
    return df.rename(columns=mapper)


def get_col_types(
    df: pd.DataFrame, categorical_curves: List[str] = None, warn: bool = True
) -> Tuple[List[str], List[str]]:
    """
    Returns lists of numerical and categorical columns

    Args:
        df (pd.DataFrame): dataframe with columns to classify
        categorical_curves (list): List of column names that should be considered as
            categorical. Defaults to an empty list.
        warn (bool): Whether to warn the user if categorical curves were
            detected which were not in the provided categorical curves list.

    Returns:
        tuple: lists of numerical and categorical columns
    """
    if categorical_curves is None:
        categorical_curves = []
    cat_original: Set[str] = set(categorical_curves)
    # Make sure we are comparing apples with apples. Sometimes cat_original
    # will contain column names that are no longer in the passed df and this
    # will cause a false positive and trigger the first if check below. So
    # ensure that all cols in cat_original are in the df before proceeding.
    cat_original = set([c for c in cat_original if c in df.columns])
    num_cols = set(df.select_dtypes(include="number").columns)
    cat_cols = set(df.columns) - num_cols
    if warn:
        if cat_cols != cat_original:
            extra = cat_original - cat_cols
            if extra:
                warnings.warn(
                    f"Cols {extra} were specified as categorical by user even though"
                    " they are numerical. Note: These column names are the names"
                    " after they have been mapped using the provided mappings.yaml!"
                    " So it could be another column from your original data that"
                    " triggered this warning and instead was mapped to one of the"
                    " names printed above."
                )
            extra = cat_cols - cat_original
            if extra:
                warnings.warn(
                    f"Cols {extra} were identified as categorical and are being"
                    " treated as such. Note: These column names"
                    " are the names after they have been mapped using the provided"
                    " mappings.yaml! So it could be another column from your"
                    " original data that triggered this warning and instead was"
                    " mapped to one of the names printed above."
                )
    cat_cols = cat_original.union(cat_cols)
    # make sure nothing from categorical is in num cols
    num_cols = num_cols - cat_cols
    return list(num_cols), list(cat_cols)


def wells_split_train_test(
    df: pd.DataFrame, id_column: str, test_size: float, **kwargs
) -> Tuple[List[str], List[str], List[str]]:
    """
    Splits wells into two groups (train and val/test)

    NOTE: Set operations are used to perform the splits so ordering is not
        preserved! The well IDs will be randomly ordered.

    Args:
        df (pd.DataFrame): dataframe with data of wells and well ID
        id_column (str): The name of the column containing well names which will
            be used to perform the split.
        test_size (float): percentage (0-1) of wells to be in val/test data

    Returns:
        wells (list): well IDs
        test_wells (list): wells IDs of val/test data
        training_wells (list): wells IDs of training data
    """
    wells = set(df[id_column].unique())
    rng: np.random.Generator = np.random.default_rng()
    test_wells = set(rng.choice(list(wells), int(len(wells) * test_size)))
    training_wells = wells - test_wells
    return list(wells), list(test_wells), list(training_wells)


def df_split_train_test(
    df: pd.DataFrame,
    id_column: str,
    test_size: float = 0.2,
    test_wells: List[str] = None,
    **kwargs,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Splits dataframe into two groups: train and val/test set.

    Args:
        df (pd.Dataframe): dataframe to split
        id_column (str): The name of the column containing well names which will
            be used to perform the split.
        test_size (float, optional): size of val/test data. Defaults to 0.2.
        test_wells (list, optional): list of wells to be in val/test data. Defaults to None.

    Returns:
        tuple: dataframes for train and test sets, and list of test well IDs
    """
    if test_wells is None:
        test_wells = wells_split_train_test(df, id_column, test_size, **kwargs)[1]
        if not test_wells:
            raise ValueError(
                "Not enough wells in your dataset to perform the requested train "
                "test split!"
            )
    df_test = df.loc[df[id_column].isin(test_wells)]
    df_train = df.loc[~df[id_column].isin(test_wells)]
    return df_train, df_test, test_wells


def train_test_split(
    df: pd.DataFrame, target_column: str, id_column: str, **kwargs
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits a dataset into training and val/test sets by well (i.e. for an
    80-20 split, the provided dataset would need data from at least 5 wells).

    This function makes use of several other utility functions. The workflow it
    executes is:

        1. Drops row without labels
        2. Splits into train and test sets using df_split_train_test which in
            turn performs the split via wells_split_train_test

    Args:
        df (pd.DataFrame, optional): dataframe with data
        target_column (str): Name of the target column (y)
        id_column (str): Name of the wells ID column. This is used to perform
            the split based on well ID.

    Keyword Args:
        test_size (float, optional): size of val/test data. Defaults to 0.2.
        test_wells (list, optional): list of wells to be in val/test data. Defaults to None.
        missing_label_value (str, optional): If nans are denoted differently than np.nans,
            a missing_label_value can be passed as a kwarg and all rows containing
            this missing_label_value in the label column will be dropped

    Returns:
        tuple: dataframes for train and test sets, and list of test wells IDs
    """
    df = drop_rows_wo_label(df, target_column, **kwargs)
    df_train, df_test, _ = df_split_train_test(df, id_column, **kwargs)
    return df_train, df_test


def feature_target_split(
    df: pd.DataFrame, target_column: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits set into features and target

    Args:
        df (pd.DataFrame): dataframe to be split
        target_column (str): target column name

    Returns:
        tuple: input (features) and output (target) dataframes
    """
    X = df.loc[:, ~df.columns.isin([target_column])]
    y = df[target_column]
    return X, y


def normalize(
    col: pd.Series, ref_min: float64, ref_max: float64, col_min: float, col_max: float
) -> pd.Series:

    """
    Helper function that applies min-max normalization on a pandas series and
    rescales it according to a reference range according to the following formula:

        ref_low + ((col - col_min) * (ref_max - ref_min) / (col_max - col_min))

    Args:
        col (pd.Series): column from dataframe to normalize (series)
        ref_low (float): min value of the column of the well of reference
        ref_high (float): max value of the column of the well of reference
        well_low (float): min value of the column of well to normalize
        well_high (float): max value of the column of well to normalize

    Returns:
        pd.Series: normalized series
    """
    diff_ref = ref_max - ref_min
    diff_well = col_max - col_min
    return ref_min + diff_ref * (col - col_min) / diff_well


def get_well_metadata(
    client: CogniteClient, well_names: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Retrieve relevant well metadata for the provided well_names

    Warning:
        If a well is not found in the asset database, it is not returned
        in the returned dictionary. Instead a warning is printed to the console
        with the corresponding well name.

    Metadata retrieved:

        - COMPLETION_DATE
        - COORD_SYSTEM_NAME
        - KB_ELEV
        - KB_ELEV_OUOM
        - PUBLIC
        - SPUD_DATE
        - WATER_DEPTH
        - CDF_wellName
        - WATER_DEPTH_DSDSUNIT
        - X_COORDINATE
        - Y_COORDINATE
        - DATUM_ELEVATION
        - DATUM_ELEVATION_UNIT
        - LATITUDE
        - LONGITUDE

    Args:
        client (CogniteClient): A connected cognite client instance
        well_names (List): The list of well names to retrieve metadata for

    Returns:
        dict: Returns a dictionary where the keys are the well names and the
            values are dictionaries with metadata keys and values.

    Example:
        Example return dictionary::

            {
                '25/10-10': {
                    'COMPLETION_DATE': '2010-04-02T00:00:00',
                    'COORD_SYSTEM_NAME': 'ED50 / UTM zone 31N',
                    'DATUM_ELEVATION': '0.0',
                    ...},
                '25/10-12 ST2': {
                    'COMPLETION_DATE': '2015-01-18T00:00:00',
                    'COORD_SYSTEM_NAME': 'ED50 / UTM zone 31N',
                    'DATUM_ELEVATION': nan,
                    ...},
            }
    """
    relevant_metadata_keys = [
        "WATER_DEPTH",
        "WATER_DEPTH_DSDSUNIT",
        "KB_ELEV",
        "KB_ELEV_OUOM",
        "PUBLIC",
        "Latitude",
        "Longitude",
        "SURFACE_NODE_LATITUDE",
        "SURFACE_NODE_LONGITUDE",
        "COORD_SYSTEM_NAME",
        "X_COORD",
        "X_COORDINATE",
        "Y_COORD",
        "Y_COORDINATE",
        "loc-x",
        "loc-y",
        "loc-x",
        "y-loc",
        "x",
        "y" "DATUM_ELEVATION",
        "DATUM_ELEVATION_DSDSUNIT",
        "DATUM_TYPE",
        "datum-elevation",
        "datum-unit",
        "SPUD_DATE",
        "COMPLETION_DATE",
        "WELLBORE_LOCATION_SPATIAL",
    ]

    map_similar_keys = {
        "X_COORDINATE": [
            "X_COORD",
            "X_COORDINATE",
            "loc-x",
            "x-loc",
        ],
        "Y_COORDINATE": [
            "Y_COORD",
            "Y_COORDINATE",
            "loc-y",
            "y-loc",
        ],
        "DATUM_ELEVATION": [
            "datum-elevation",
            "DATUM_ELEVATION",
        ],
        "DATUM_ELEVATION_UNIT": [
            "datum-unit",
            "DATUM_ELEVATION_DSDS_UNIT",
        ],
        "LATITUDE": [
            "Latitude",
            "SURFACE_NODE_LATITUDE",
            "y",
        ],
        "LONGITUDE": [
            "Longitude",
            "SURFACE_NODE_LONGITUDE",
            "x",
        ],
    }

    # Helper function to find best match from fuzzy search results
    def _find_best_match(assetlist: AssetList, wellName: str) -> str:
        # Compares only the alphanumerics of the wellName (ie. punctuation removed)
        # If no match is found it returns an empty string
        pat = re.compile(r"[\W_]+")
        for asset in assetlist:
            name: str = asset.name
            if pat.sub("", name) == pat.sub("", wellName):
                return name
        return wellName

    # Helper function to retrieve asset with most relevant metadata in the case
    # of multiple matches
    def _merge_assets(assetlist: List[Asset]) -> pd.Series:
        metadata = {}
        for asset in assetlist:
            metadata.update(asset.to_pandas().squeeze().to_dict())

        merged = pd.Series(metadata, name=metadata["name"])
        return merged

    # First retrieve metadata from the Cognite asset API
    meta = []
    for well in well_names:
        try:
            # First try list search
            asset: Union[AssetList, List[Asset], Asset] = client.assets.list(name=well)
            if len(asset) == 0:
                # If first attempt failed use fuzzy search to retrieve proper
                # well name. Trust the fuzzy searches top result as a match with the well
                # is this safe?
                wellName = _find_best_match(
                    client.assets.search(name=well, limit=10), well
                )
                warnings.warn(
                    f"Could not find a direct match for '{well}' in the CDF Assets"
                    f" database. Closest match found is '{wellName}'. Using the "
                    "metadata from that asset!"
                )
                # Then retrieve asset using list API
                asset = client.assets.list(name=wellName)
            if len(asset) > 1:
                # Sort by time with first element being most recent
                asset = sorted(asset, key=lambda x: x.last_updated_time)
                # Some wells are stored several times as assets??
                # In this case find the entry which has the most matches in
                # metadata keys that we want
                series_meta = _merge_assets(asset)
            else:
                asset = asset[0]
                series_meta = asset.to_pandas().squeeze()
                series_meta.name = asset.name
        except IndexError:
            # No match found for the well in the asset database.
            warnings.warn(f"Could not find any metadata for well: {well}")
            continue

        # Filter retrieved series to only relevant keys and save CDF well name
        series_meta = series_meta.loc[
            series_meta.index.intersection(relevant_metadata_keys)
        ].copy()
        series_meta.loc["CDF_wellName"] = series_meta.name
        series_meta.name = well

        meta.append(series_meta)

    cdf_meta = pd.concat(meta, axis=1)

    # Need to handle WELLBORE_LOCATION_SPATIAL specially
    if "WELLBORE_LOCATION_SPATIAL" in cdf_meta.index:
        sub = cdf_meta.loc["WELLBORE_LOCATION_SPATIAL"].dropna().apply(eval).copy()
        restructured = pd.json_normalize(sub)[["x", "y"]]
        restructured.index = sub.index
        restructured = restructured.explode("x").explode("y").T
        cdf_meta = pd.concat([cdf_meta, restructured], axis=0)
        cdf_meta = cdf_meta.loc[~cdf_meta.index.isin(["WELLBORE_LOCATION_SPATIAL"])]

    # Then group mapped keys
    # Helper function for apply operation
    def _apply_function(x: pd.Series) -> Any:
        unique = x.dropna().unique()
        if len(unique) > 1:
            # Check for multiple unique values per well
            raise ValueError(
                "At least two unique values were found for the same metadata"
                f" field! Problematic well {x.name}: \n {x.to_string()}"
            )
        elif len(unique) == 0:
            return np.nan
        else:
            return unique[0]

    for mapping_name, mapping in map_similar_keys.items():
        # filter to relevant mapping
        idx = cdf_meta.index.intersection(mapping)
        if len(idx) == 0:  # No metadata matching this mapping
            continue
        elif len(idx) == 1:  # One key matching this mapping so just use it's values
            values = cdf_meta.loc[idx].squeeze()
        else:
            values = cdf_meta.loc[idx].apply(_apply_function, axis=0)
            values.name = mapping_name
        cdf_meta = cdf_meta.loc[~cdf_meta.index.isin(idx)]
        cdf_meta.loc[mapping_name] = values

    metadata_dict: Dict[str, Dict[str, Any]] = cdf_meta.to_dict()
    return metadata_dict


def get_formation_tops(
    well_names: str,
    client: CogniteClient,
    **kwargs,
) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves formation tops metadata for a provided list of well names (IDs) from
    CDF and returns them in a dictionary of depth levels and labels per well.

    Args:
        well_names (str): A list of well names (IDs)
        client (CogniteClient): A connected instance of the Cognite Client.

    Keyword Args:
        undefined_name (str): Name for undefined formation/group tops.
            Defaults to 'UNKNOWN'

    NOTE: The formation will be skipped if it's only 1m thick.
            NPD do not provide technial side tracks,
            such that information (formation tops) provided
            by NPD is missing T-labels.

    Returns:
        Dict: Returns a dictionary of formation tops metadata per map in this
            format::

                formation_tops_mapper = {
                    "31/6-6": {
                        "group_labels": ['Nordland Group', 'Hordaland Group', ...],
                        "group_labels_chronostrat": ['Cenozoic', 'Paleogene', ...]
                        "group_levels": [336.0, 531.0, 650.0, ...],
                        "formation_labels": ['Balder Formation', 'Sele Formation', ...],
                        "formation_labels_chronostrat": ['Eocene', 'Paleocene', ...],
                        "formation_levels": [650.0, 798.0, 949.0, ...]
                    }
                    ...
                }
    NOTE: The length of the levels entries equals the length of the corresponding labels entries + 1,
            such that the first entry of a label entry lies between the first and the second entries
            of the corresponding level entry.
    """
    undefined_name: str = kwargs.get("undefined_name", "UNKNOWN")

    formation_tops_mapper = {}
    for well in well_names:
        well_name = well.split("T")[0].strip()

        tops = client.sequences.list(
            metadata={
                "wellbore_name": well_name,
                "type": "FormationTops",
                "source": "NPD",
            }
        )
        if tops is None or len(tops) == 0:
            continue
        rows = tops[0].rows(start=None, end=None).to_pandas()

        rows_groups = rows[rows.Level == "GROUP"].sort_values(["Top_MD", "Base_MD"])
        rows_formations = rows[rows.Level == "FORMATION"].sort_values(
            ["Top_MD", "Base_MD"]
        )

        group_labels: List[str] = []
        chrono_group_labels: List[str] = []
        group_levels: List[float] = []
        formation_labels: List[str] = []
        chrono_formation_labels: List[str] = []
        formation_levels: List[float] = []
        label = undefined_name

        ### Groups ###
        for _, row in rows_groups.iterrows():
            # Skip group is length is 1m
            if row.Top_MD == row.Base_MD:
                continue
            new_label = row.Lithostrat
            new_chrono_label = row.Chronostrat

            if label == new_label or new_label.lower().startswith(
                "undefined"
            ):  # merge levels
                group_levels = group_levels[:-1]
                group_levels.append(row.Base_MD)
            else:
                try:
                    if row.Top_MD != group_levels[-1]:  # groups not continuous
                        group_labels.append(undefined_name)
                        chrono_group_labels.append(undefined_name)
                        group_levels.extend([group_levels[-1], row.Top_MD])
                except Exception:
                    pass
                label = new_label
                chrono_label = new_chrono_label
                group_labels.append(label)
                chrono_group_labels.append(chrono_label)
                group_levels.extend([row.Top_MD, row.Base_MD])
        group_levels = list(dict.fromkeys(group_levels))
        assert len(chrono_group_labels) == len(
            group_labels
        ), "Chronostrat labels no consistent with groups"

        ### Formations ###
        label = undefined_name
        for _, row in rows_formations.iterrows():
            # Skip formation is length is 1m
            if row.Top_MD == row.Base_MD:
                continue
            new_label = row.Lithostrat
            new_chrono_label = row.Chronostrat
            if label == new_label or new_label.lower().startswith("undefined"):
                formation_levels = formation_levels[:-1]
                formation_levels.append(row.Base_MD)
            else:
                try:
                    if row.Top_MD != formation_levels[-1]:  # groups not continuous
                        formation_labels.append(undefined_name)
                        chrono_formation_labels.append(undefined_name)
                        formation_levels.extend([formation_levels[-1], row.Top_MD])
                except Exception:
                    pass
                label = new_label
                chrono_label = new_chrono_label
                formation_labels.append(label)
                chrono_formation_labels.append(chrono_label)
                formation_levels.extend([row.Top_MD, row.Base_MD])
        formation_levels = list(dict.fromkeys(formation_levels))
        assert len(chrono_formation_labels) == len(
            formation_labels
        ), "Chronostrat labels no consistent with formations"

        formation_tops_mapper[well] = {
            "group_labels": group_labels,
            "group_labels_chronostrat": chrono_group_labels,
            "group_levels": group_levels,
            "formation_labels": formation_labels,
            "formation_labels_chronostrat": chrono_formation_labels,
            "formation_levels": formation_levels,
        }
    return formation_tops_mapper
