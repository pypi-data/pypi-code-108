import math
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from go_utils.cleanup import (
    camel_case,
    remove_homogenous_cols,
    rename_latlon_cols,
    replace_column_prefix,
    round_cols,
    standardize_null_vals,
)
from go_utils.plot import completeness_histogram, multiple_bar_graph, plot_freq_bar

__doc__ = """

## Unpacking the Landcover Classification Data
The classification data for each entry is condensed into several entries separated by a semicolon. [This method](#unpack_classifications) identifies and parses Land Cover Classifications and percentages to create new columns. The columns are also reordered to better group directional information together.

The end result is a DataFrame that contains columns for every Unique Landcover Classification (per direction) and its respective percentages for each entry.

There are four main steps to this procedure:
1.Identifying Land Cover Classifications for each Cardinal Direction: An internal method returns the unique description (e.g. HerbaceousGrasslandTallGrass) listed in a column. This method is run for all 4 cardinal directions to obtain the all unique classifications per direction.
2. Creating empty columns for each Classification from each Cardinal Direction: Using the newly identified classifications new columns are made for each unique classification. These columns initially contained the default float64 value of 0.0. By initializing all the classification column values to 0.0, we ensure no empty values are set to -9999 in the round_cols(df) method (discussed in General Cleanup Procedures - Round Appropriate Columns). This step eases future numerical analysis.
3. Grouping and Alphabetically Sorting Directional Column Information: To better organize the DataFrame, columns containing any of the following directional substrings: "downward", "upward", "west", "east", "north", "south" (case insensitive) are identified and alphabetically sorted. Then an internal method called move_cols, specified column headers to move (direction_data_cols), and the location before the desired point of insertion, the program returns a reordered DataFrame, where all directional columns are grouped together. This greatly improves the Land Covers dataset’s organization and accessibility.
4. Adding Classification Percentages to their respective Land Cover Classification Columns - To fill in each classification column with their respective percentages, an internal method is applied to each row in the dataframe. This method iterates through each classification direction (ie “lc_EastClassifications”) and sets each identified Classification column with its respective percentage.

NOTE: After these procedures, the original directional classification columns (e.g. “lc_EastClassifications”) are not dropped.
"""

classifications = []


def cleanup_column_prefix(df, inplace=False):
    """Method for shortening raw landcover column names.

    The df object will now replace the verbose `landcovers` prefix in some of the columns with `lc_`

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing raw landcover data. The DataFrame object itself will be modified.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the cleaned up column prefixes. If `inplace=True` it returns None.
    """

    if not inplace:
        df = df.copy()

    replace_column_prefix(df, "landcovers", "lc", inplace=True)

    if not inplace:
        return df


def extract_classification_name(entry):
    """
    Extracts the name (landcover description) of a singular landcover classification. For example in the classification of `"60% MUC 02 (b) [Trees, Closely Spaced, Deciduous - Broad Leaved]"`, the `"Trees, Closely Spaced, Deciduous - Broad Leaved"` is extracted.

    Parameters
    ----------
    entry : str
        A single landcover classification.

    Returns
    -------
    str
        The Landcover description of a classification
    """

    return re.search(r"(?<=\[).*(?=\])", entry).group()


def extract_classification_percentage(entry):
    """
    Extracts the percentage of a singular landcover classification. For example in the classification of `"60% MUC 02 (b) [Trees, Closely Spaced, Deciduous - Broad Leaved]"`, the `60` is extracted.

    Parameters
    ----------
    entry : str
        A single landcover classification.

    Returns
    -------
    float
        The percentage of a landcover classification
    """

    return float(re.search(".*(?=%)", entry).group())


def _extract_landcover_items(func, info):
    entries = info.split(";")
    return [func(entry) for entry in entries]


def extract_classifications(info):
    """Extracts the name/landcover description (see [here](#extract_classification_name) for a clearer definition) of a landcover classification entry in the GLOBE Observer Data.

    Parameters
    ----------
    info : str
        A string representing a landcover classification entry in the GLOBE Observer Datset.

    Returns
    -------
    list of str
        The different landcover classifications stored within the landcover entry.
    """
    return _extract_landcover_items(extract_classification_name, info)


def extract_percentages(info):
    """Extracts the percentages (see [here](#extract_classification_percentage) for a clearer definition) of a landcover classification in the GLOBE Observer Datset.

    Parameters
    ----------
    info : str
        A string representing a landcover classification entry in the GLOBE Observer Datset.

    Returns
    -------
    list of float
        The different landcover percentages stored within the landcover entry.
    """

    return _extract_landcover_items(extract_classification_percentage, info)


def extract_classification_dict(info):
    """Extracts the landcover descriptions and percentages of a landcover classification entry as a dictionary.

    Parameters
    ----------
    info : str
        A string representing a landcover classification entry in the GLOBE Observer Datset.

    Returns
    -------
    dict of str, float
        The landcover descriptions and percentages stored as a dict in the form: `{"description" : percentage}`.
    """

    entries = info.split(";")
    return {
        extract_classification_name(entry): extract_classification_percentage(entry)
        for entry in entries
    }


def _get_classifications_for_direction(df, direction_col_name):
    list_of_land_types = []
    for info in df[direction_col_name]:
        # Note: Sometimes info = np.nan, a float -- In that case we do NOT parse/split
        if type(info) == str:
            [
                list_of_land_types.append(camel_case(entry, [" ", ",", "-", "/"]))
                for entry in extract_classifications(info)
            ]
    return np.unique(list_of_land_types).tolist()


def _move_cols(df, cols_to_move=[], ref_col=""):
    col_names = df.columns.tolist()
    index_before_desired_loc = col_names.index(ref_col)

    cols_before_index = col_names[: index_before_desired_loc + 1]
    cols_at_index = cols_to_move

    cols_before_index = [i for i in cols_before_index if i not in cols_at_index]
    cols_after_index = [
        i for i in col_names if i not in cols_before_index + cols_at_index
    ]

    return df[cols_before_index + cols_at_index + cols_after_index]


def unpack_classifications(
    lc_df,
    north="lc_NorthClassifications",
    east="lc_EastClassifications",
    south="lc_SouthClassifications",
    west="lc_WestClassifications",
    ref_col="lc_pid",
    unpack=True,
):
    """
    Unpacks the classification data in the *raw* GLOBE Observer Landcover data. This method assumes that the columns have been renamed with accordance to the [column cleanup](#cleanup_column_prefix) method.

    This returns a copy of the dataframe.

    See [here](#unpacking-the-landcover-classification-data) for more information.

    *Note:* The returned DataFrame will have around 250 columns.

    Parameters
    ----------
    lc_df : pd.DataFrame
        A DataFrame containing Raw GLOBE Observer Landcover data that has had the column names simplified.
    north: str, default="lc_NorthClassifications"
        The name of the column which contains the North Classifications
    east: str, default="lc_EastClassifications"
        The name of the column which contains the East Classifications
    south: str, default="lc_SouthClassifications"
        The name of the column which contains the South Classifications
    west: str, default="lc_WestClassifications"
        The name of the column which contains the West Classifications
    ref_col: str, default="lc_pid"
        The name of the column which all of the expanded values will be placed after. For example, if the columns were `[1, 2, 3, 4]` and you chose 3, the new columns will now be `[1, 2, 3, (all classification columns), 4]`.
    unpack: bool, default=True
        True if you want to unpack the directional classifications, False if you only want overall classifications

    Returns
    -------
    pd.DataFrame
        A DataFrame with the unpacked classification columns.
    list
        A list containing all the generated overall Land Cover column names (mainly for testing purposes).
    list
        A list containing all the generated directional Land Cover column names (mainly for testing purposes).
    """

    classifications = [north, east, south, west]

    def set_directions(row):
        for classification in classifications:
            if not pd.isnull(row[classification]):
                entries = row[classification].split(";")
                for entry in entries:
                    percent, name = (
                        extract_classification_percentage(entry),
                        extract_classification_name(entry),
                    )
                    name = camel_case(name, [" ", ",", "-", "/"])
                    classification = classification.replace("Classifications", "_")
                    overall = re.sub(
                        r"(north|south|east|west).*",
                        "Overall_",
                        key,
                        flags=re.IGNORECASE,
                    )
                    row[f"{classification}{name.strip()}"] = percent
                    row[f"{overall}{name.strip()}"] += percent
        return row

    land_type_columns_to_add = {
        classification: _get_classifications_for_direction(lc_df, classification)
        for classification in classifications
    }
    overall_columns = set()
    direction_cols = set()
    for key, values in land_type_columns_to_add.items():
        direction_name = key.replace("Classifications", "_")
        overall = re.sub(
            r"(north|south|east|west).*", "Overall_", key, flags=re.IGNORECASE
        )
        for value in values:
            direction_cols.add(direction_name + value)
            overall_columns.add(overall + value)
    overall_columns = list(overall_columns)
    direction_cols = list(direction_cols)
    direction_data_cols = sorted(overall_columns + direction_cols)

    # Creates a blank DataFrame and concats it to the original to avoid iteratively growing the LC DataFrame
    blank_df = pd.DataFrame(
        np.zeros((len(lc_df), len(direction_data_cols))), columns=direction_data_cols
    )

    lc_df = pd.concat([lc_df, blank_df], axis=1)

    lc_df = _move_cols(lc_df, cols_to_move=direction_data_cols, ref_col=ref_col)
    lc_df = lc_df.apply(set_directions, axis=1)
    for column in overall_columns:
        lc_df[column] /= 4

    if not unpack:
        lc_df = lc_df.drop(columns=direction_cols)
    return lc_df, overall_columns, direction_cols


def photo_bit_flags(
    df,
    up="lc_UpwardPhotoUrl",
    down="lc_DownwardPhotoUrl",
    north="lc_NorthPhotoUrl",
    south="lc_SouthPhotoUrl",
    east="lc_EastPhotoUrl",
    west="lc_WestPhotoUrl",
    photo_count="lc_PhotoCount",
    rejected_count="lc_RejectedCount",
    pending_count="lc_PendingCount",
    empty_count="lc_EmptyCount",
    bit_binary="lc_PhotoBitBinary",
    bit_decimal="lc_PhotoBitDecimal",
    inplace=False,
):
    """
    Creates the following flags:
    - `PhotoCount`: The number of valid photos per record.
    - `RejectedCount`: The number of photos that were rejected per record.
    - `PendingCount`: The number of photos that are pending approval per record.
    - `PhotoBitBinary`: A string that represents the presence of a photo in the Up, Down, North, South, East, and West directions. For example, if the entry is `110100`, that indicates that there is a valid photo for the Up, Down, and South Directions but no valid photos for the North, East, and West Directions.
    - `PhotoBitDecimal`: The numerical representation of the lc_PhotoBitBinary string.

    Parameters
    ----------
    df : pd.DataFrame
        A land cover DataFrame
    up : str, default="lc_UpwardPhotoUrl"
        The name of the column in the land cover DataFrame that contains the url for the upwards photo.
    down : str, default="lc_DownwardPhotoUrl"
        The name of the column in the land cover DataFrame that contains the url for the downwards photo.
    north : str, default="lc_NorthPhotoUrl"
        The name of the column in the land cover DataFrame that contains the url for the north photo.
    south : str, default="lc_SouthPhotoUrl"
        The name of the column in the land cover DataFrame that contains the url for the south photo.
    east : str, default="lc_EastPhotoUrl"
        The name of the column in the land cover DataFrame that contains the url for the east photo.
    west : str, default="lc_WestPhotoUrl"
        The name of the column in the land cover DataFrame that contains the url for the west photo.
    photo_count : str, default="lc_PhotoCount"
        The name of the column that will be storing the PhotoCount flag.
    rejected_count : str, default="lc_RejectedCount"
        The name of the column that will be storing the RejectedCount flag.
    pending_count : str, default="lc_PendingCount"
        The name of the column that will be storing the PendingCount flag.
    empty_count : str, default="lc_EmptyCount"
        The name of the column that will be storing the EmptyCount flag.
    bit_binary : str, default="lc_PhotoBitBinary"
        The name of the column that will be storing the PhotoBitBinary flag.
    bit_decimal : str, default="lc_PhotoBitDecimal"
        The name of the column that will be storing the PhotoBitDecimal flag.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the photo bit flags. If `inplace=True` it returns None.
    """

    def pic_data(*args):
        pic_count = 0
        rejected_count = 0
        pending_count = 0
        empty_count = 0
        valid_photo_bit_mask = ""

        for entry in args:
            if not pd.isna(entry) and "http" in entry:
                valid_photo_bit_mask += "1"
                pic_count += entry.count("http")
            else:
                valid_photo_bit_mask += "0"
            if pd.isna(entry):
                empty_count += 1
            else:
                pending_count += entry.count("pending")
                rejected_count += entry.count("rejected")
        return (
            pic_count,
            rejected_count,
            pending_count,
            empty_count,
            valid_photo_bit_mask,
            int(valid_photo_bit_mask, 2),
        )

    if not inplace:
        df = df.copy()

    get_photo_data = np.vectorize(pic_data)
    (
        df[photo_count],
        df[rejected_count],
        df[pending_count],
        df[empty_count],
        df[bit_binary],
        df[bit_decimal],
    ) = get_photo_data(
        df[up].to_numpy(),
        df[down].to_numpy(),
        df[north].to_numpy(),
        df[south].to_numpy(),
        df[east].to_numpy(),
        df[west].to_numpy(),
    )

    if not inplace:
        return df


def classification_bit_flags(
    df,
    north="lc_NorthClassifications",
    south="lc_SouthClassifications",
    east="lc_EastClassifications",
    west="lc_WestClassifications",
    classification_count="lc_ClassificationCount",
    bit_binary="lc_ClassificationBitBinary",
    bit_decimal="lc_ClassificationBitDecimal",
    inplace=False,
):
    """
    Creates the following flags:
    - `ClassificationCount`: The number of classifications per record.
    - `BitBinary`: A string that represents the presence of a classification in the North, South, East, and West directions. For example, if the entry is `1101`, that indicates that there is a valid classification for the North, South, and West Directions but no valid classifications for the East Direction.
    - `BitDecimal`: The number of photos that are pending approval per record.

    Parameters
    ----------
    df : pd.DataFrame
        A land cover DataFrame
    north : str, default="lc_NorthClassifications"
        The name of the column in the land cover DataFrame that contains the north classification.
    south : str, default="lc_SouthClassifications"
        The name of the column in the land cover DataFrame that contains the south classification.
    east : str, default="lc_EastClassifications"
        The name of the column in the land cover DataFrame that contains the east classification.
    west : str, default="lc_WestClassifications"
        The name of the column in the land cover DataFrame that contains the west classification.
    classification_count : str, default="lc_ClassificationCount"
        The name of the column that will store the ClassificationCount flag.
    bit_binary : str, default="lc_ClassificationBitBinary"
        The name of the column that will store the BitBinary flag.
    bit_decimal : str, default="lc_ClassificationBitDecimal"
        The name of the column that will store the BitDecimal flag.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the classification bit flags. If `inplace=True` it returns None.
    """

    def classification_data(*args):
        classification_count = 0
        classification_bit_mask = ""
        for entry in args:
            if pd.isna(entry) or entry is np.nan:
                classification_bit_mask += "0"
            else:
                classification_count += 1
                classification_bit_mask += "1"
        return (
            classification_count,
            classification_bit_mask,
            int(classification_bit_mask, 2),
        )

    if not inplace:
        df = df.copy()
    get_classification_data = np.vectorize(classification_data)

    (
        df[classification_count],
        df[bit_binary],
        df[bit_decimal],
    ) = get_classification_data(
        df[north],
        df[south],
        df[east],
        df[west],
    )
    if not inplace:
        return df


def completion_scores(
    df,
    photo_bit_binary="lc_PhotoBitBinary",
    classification_binary="lc_ClassificationBitBinary",
    sub_completeness="lc_SubCompletenessScore",
    completeness="lc_CumulativeCompletenessScore",
    inplace=False,
):
    """
    Adds the following completness score flags:
    - `SubCompletenessScore`: The percentage of valid landcover classifications and photos that are filled out.
    - `CumulativeCompletenessScore`: The percentage of non null values out of all the columns.

    Parameters
    ----------
    df : pd.DataFrame
        A landcover DataFrame with the [`PhotoBitBinary`](#photo_bit_flags) and [`ClassificationBitBinary`](#classification_bit_flags) flags.
    photo_bit_binary : str, default="lc_PhotoBitBinary"
        The name of the column that stores the PhotoBitBinary flag.
    classification_binary : str, default="lc_PhotoBitBinary"
        The name of the column that stores the ClassificationBitBinary flag.
    sub_completeness : str, default="lc_PhotoBitBinary"
        The name of the column that will store the generated SubCompletenessScore flag.
    completeness : str, default="lc_PhotoBitBinary"
        The name of the column that will store the generated CompletenessScore flag.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the completeness score flags. If `inplace=True` it returns None.
    """

    def sum_bit_mask(bit_mask="0"):
        sum = 0.0
        for char in bit_mask:
            sum += int(char)
        return sum

    if not inplace:
        df = df.copy()

    scores = {}
    scores["sub_score"] = []
    # Cummulative Completion Score
    scores["cumulative_score"] = round(df.count(1) / len(df.columns), 2)
    # Sub-Score
    for index in df.index:
        bit_mask = df[photo_bit_binary][index] + df[classification_binary][index]
        sub_score = round(sum_bit_mask(bit_mask=bit_mask), 2)
        sub_score /= len(bit_mask)
        scores["sub_score"].append(sub_score)

    df[sub_completeness], df[completeness] = (
        scores["sub_score"],
        scores["cumulative_score"],
    )

    if not inplace:
        return df


def apply_cleanup(lc_df, unpack=True):
    """Applies a full cleanup procedure to the landcover data.
    It follows the following steps:
    - Removes Homogenous Columns
    - Renames Latitude and Longitudes
    - Cleans the Column Naming
    - Unpacks landcover classifications
    - Rounds Columns
    - Standardizes Null Values

    This returns a copy

    Parameters
    ----------
    lc_df : pd.DataFrame
        A DataFrame containing **raw** Landcover Data from the API.
    unpack : bool
        If True, the Landcover data will expand the classifications into separate columns (results in around 300 columns). If False, it will just unpack overall landcover.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the cleaned Landcover Data
    """
    lc_df = lc_df.copy()

    remove_homogenous_cols(lc_df, inplace=True)
    rename_latlon_cols(lc_df, inplace=True)
    cleanup_column_prefix(lc_df, inplace=True)
    lc_df, overall_cols, directional_cols = unpack_classifications(lc_df, unpack=unpack)

    round_cols(lc_df, inplace=True)
    standardize_null_vals(lc_df, inplace=True)
    return lc_df


def add_flags(lc_df):
    """Adds the following flags to the landcover data:
    - Photo Bit Flags
    - Classification Bit Flags
    - Completeness Score Flags

    Returns a copy of the DataFrame

    Parameters
    ----------
    lc_df : pd.DataFrame
        A DataFrame containing cleaned up Landcover Data ideally from the [apply_cleanup](#apply_cleanup) method.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the Land Cover flags.
    """
    lc_df = lc_df.copy()
    photo_bit_flags(lc_df, inplace=True)
    classification_bit_flags(lc_df, inplace=True)
    get_main_classifications(lc_df, inplace=True)
    completion_scores(lc_df, inplace=True)
    return lc_df


def direction_frequency(lc_df, direction_list, bit_binary, entry_type):
    """
    Plots the amount of a variable of interest for each direction.

    Parameters
    ----------
    lc_df : pd.DataFrame
        The DataFrame containing Land Cover Data.
    direction_list : list of str
        The column names of the different variables of interest for each direction.
    bit_binary: str
        The Bit Binary Flag associated with the variable of interest.
    entry_type: str
        The variable of interest (e.g. Photos or Classifications)
    """
    direction_photos = pd.DataFrame()
    direction_photos["category"] = direction_list
    direction_counts = [0 for i in range(len(direction_photos))]
    for mask in lc_df[bit_binary]:
        for i in range(len(mask) - 1, -1, -1):
            direction_counts[i] += int(mask[i])
    direction_counts
    direction_photos["count"] = [math.log10(value) for value in direction_counts]
    direction_photos

    plt.figure(figsize=(15, 6))
    title = f"Land Cover -- {entry_type} Direction Frequency (Log Scale)"
    plt.title(title)
    plt.ylabel("Count (Log Scale)")
    sns.barplot(data=direction_photos, x="category", y="count", color="lightblue")


def diagnostic_plots(
    lc_df,
    up_url="lc_UpwardPhotoUrl",
    down_url="lc_DownwardPhotoUrl",
    north_url="lc_NorthPhotoUrl",
    south_url="lc_SouthPhotoUrl",
    east_url="lc_EastPhotoUrl",
    west_url="lc_WestPhotoUrl",
    photo_bit="lc_PhotoBitBinary",
    north_classification="lc_NorthClassifications",
    south_classification="lc_SouthClassifications",
    east_classification="lc_EastClassifications",
    west_classification="lc_WestClassifications",
    classification_bit="lc_ClassificationBitBinary",
):
    """
    Generates (but doesn't display) diagnostic plots to gain insight into the current data.

    Plots:
    - Valid Photo Count Distribution
    - Photo Distribution by direction
    - Classification Distribution by direction
    - Photo Status Distribution
    - Completeness Score Distribution
    - Subcompleteness Score Distribution

    Parameters
    ----------
    lc_df : pd.DataFrame
        The DataFrame containing Flagged and Cleaned Land Cover Data.
    """
    plot_freq_bar(
        lc_df, "Land Cover", "lc_PhotoCount", "Valid Photo Count", log_scale=True
    )
    direction_frequency(
        lc_df,
        [up_url, down_url, north_url, south_url, east_url, west_url],
        photo_bit,
        "Photo",
    )
    direction_frequency(
        lc_df,
        [
            north_classification,
            south_classification,
            east_classification,
            west_classification,
        ],
        classification_bit,
        "Classification",
    )
    multiple_bar_graph(
        lc_df,
        "Land Cover",
        ["lc_PhotoCount", "lc_RejectedCount", "lc_EmptyCount"],
        "Photo Summary",
        log_scale=True,
    )

    completeness_histogram(
        lc_df, "Land Cover", "lc_CumulativeCompletenessScore", "Cumulative Completeness"
    )
    completeness_histogram(
        lc_df, "Land Cover", "lc_SubCompletenessScore", "Sub Completeness"
    )


def qa_filter(
    lc_df,
    has_classification=False,
    has_photo=False,
    has_all_photos=False,
    has_all_classifications=False,
):
    """
    Can filter a cleaned and flagged mosquito habitat mapper DataFrame based on the following criteria:
    - `Has Classification`: If the entry has atleast one direction classified
    - `Has Photo` : If the entry has atleast one photo taken
    - `Has All Photos` : If the entry has all photos taken (up, down, north, south, east, west)
    - `Has All Classifications` : If the entry has all directions classified

    Returns a copy of the DataFrame

    Parameters
    ----------
    has_classification : bool, default=False
        If True, only entries with atleast one classification will be included.
    has_photo : bool, default=False
        If True, only entries with atleast one photo will be included.
    has_all_photos : bool, default=False
        If True, only entries with all photos will be included.
    has_all_classifications : bool, default=False
        If True, only entries with all classifications will be included.

    Returns
    -------
    pd.DataFrame
        A DataFrame of the applied filters.
    """

    if has_classification and not has_all_classifications:
        lc_df = lc_df[lc_df["lc_ClassificationBitDecimal"] > 0]
    elif has_all_classifications:
        lc_df = lc_df[lc_df["lc_ClassificationBitDecimal"] == 15]
    if has_photo and not has_all_photos:
        lc_df = lc_df[lc_df["lc_PhotoBitDecimal"] > 0]
    elif has_all_photos:
        lc_df = lc_df[lc_df["lc_PhotoBitDecimal"] == 63]

    return lc_df


def _accumulate_ties(classification_list):
    classifications = list()
    i = 0
    while i < len(classification_list) - 1:
        if classification_list[i][1] == classification_list[i + 1][1]:
            classifications.append(classification_list[i][0])
            classifications.append(classification_list[i + 1][0])
            i += 1
        else:
            break

    output = ", ".join([classification for classification in classifications])
    if not output:
        if len(classification_list) != 0:
            output = classification_list[0][0]
        else:
            output = "NA"
    # TODO replace w regex methods
    return output, i + 1


def _rank_direction(classification_dict, direction_classifications):
    if pd.isna(direction_classifications):
        return "NA", "NA"
    classifications_list = []
    classifications = direction_classifications.split(";")
    for classification_data in classifications:
        percent = extract_classification_percentage(classification_data)
        classification = extract_classification_name(classification_data)
        if classification in classification_dict:
            classification_dict[classification] += percent
        else:
            classification_dict[classification] = percent
        classifications_list.append((classification, percent))
    classifications_list = sorted(
        classifications_list, key=lambda x: x[1], reverse=True
    )
    if len(classifications_list) < 2:
        return classifications_list[0][0], "NA"

    primary_classification, i = _accumulate_ties(classifications_list)
    secondary_classification, temp = _accumulate_ties(classifications_list[i:])

    return primary_classification, secondary_classification


def _rank_classifications(*args):
    classification_dict = {}
    rank_directions = [
        classification
        for arg in args
        for classification in _rank_direction(classification_dict, arg)
    ]
    primary, secondary = ("NA", 0), ("NA", 0)
    if classification_dict:
        if len(classification_dict) < 2:
            primary = (
                list(classification_dict.keys())[0],
                list(classification_dict.values())[0],
            )
        else:
            sorted_classifications = sorted(
                classification_dict.items(), key=lambda x: x[1], reverse=True
            )
            primary, i = _accumulate_ties(sorted_classifications)
            primary = primary, sorted_classifications[0][1]
            if i < len(sorted_classifications):
                secondary, temp = _accumulate_ties(sorted_classifications[i:])
                secondary = secondary, sorted_classifications[i][1]
    return (
        *rank_directions,
        primary[0],
        secondary[0],
        primary[1] / len(args),
        secondary[1] / len(args),
    )


def get_main_classifications(
    lc_df,
    north_classification="lc_NorthClassifications",
    east_classification="lc_EastClassifications",
    south_classification="lc_SouthClassifications",
    west_classification="lc_WestClassifications",
    north_primary="lc_NorthPrimary",
    north_secondary="lc_NorthSecondary",
    east_primary="lc_EastPrimary",
    east_secondary="lc_EastSecondary",
    south_primary="lc_SouthPrimary",
    south_secondary="lc_SouthSecondary",
    west_primary="lc_WestPrimary",
    west_secondary="lc_WestSecondary",
    primary_classification="lc_PrimaryClassification",
    secondary_classification="lc_SecondaryClassification",
    primary_percentage="lc_PrimaryPercentage",
    secondary_percentage="lc_SecondaryPercentage",
    inplace=False,
):
    if not inplace:
        lc_df = lc_df.copy()
    vectorized_rank = np.vectorize(_rank_classifications)
    (
        lc_df[north_primary],
        lc_df[north_secondary],
        lc_df[east_primary],
        lc_df[east_secondary],
        lc_df[south_primary],
        lc_df[south_secondary],
        lc_df[west_primary],
        lc_df[west_secondary],
        lc_df[primary_classification],
        lc_df[secondary_classification],
        lc_df[primary_percentage],
        lc_df[secondary_percentage],
    ) = vectorized_rank(
        lc_df[north_classification].to_numpy(),
        lc_df[east_classification].to_numpy(),
        lc_df[south_classification].to_numpy(),
        lc_df[west_classification].to_numpy(),
    )

    if not inplace:
        return lc_df
