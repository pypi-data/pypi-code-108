import math
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from go_utils.cleanup import (
    rename_latlon_cols,
    replace_column_prefix,
    round_cols,
    standardize_null_vals,
)
from go_utils.plot import completeness_histogram, plot_freq_bar, plot_int_distribution

__doc__ = r"""

## Mosquito Specific Cleanup Procedures

### Converting Larvae Data to Integers
Larvae Data is stored as a string in the raw GLOBE Observer dataset. To facillitate analysis, [this method](#larvae_to_num) converts this data to numerical data.

It needs to account for 4 types of data:
1. Regular Data: Converts it to a number
2. Extraneously large data ($\geq 100$ as its hard to count more than that amount accurately): To maintain the information from that entry, the `LarvaeCountMagnitude` flag is used to indicate the real value
3. Ranges (e.g. "25-50"): Chooses the lower bound and set the `LarvaeCountIsRangeFlag` to true.
4. Null Values: Sets null values to $-9999$


It generates the following flags:
- `LarvaeCountMagnitude`: The integer flag contains the order of magnitude (0-4) by which the larvae count exceeds the maximum Larvae Count of 100. This is calculated by $1 + \lfloor \log{\frac{num}{100}} \rfloor$. As a result:
    - `0`: Corresponds to a Larvae Count $\leq 100$
    - `1`: Corresponds to a Larvae Count between $100$ and $999$
    - `2`: Corresponds to a Larvae Count between $1000$ and $9999$
    - `3`: Corresponds to a Larvae Count between $10,000$ and $99,999$
    - `4`: Corresponds to a Larvae Count $\geq 100,000$
- `LarvaeCountIsRange`: Either a $1$ which indicates the entry was a range (e.g. 25-50) or $0$ which indicates the entry wasn't a range.

Additionally, there were extremely large values that Python was unable to process (`1e+27`) and so there was an initial preprocessing step to set those numbers to 100000 (which corresponds to the maximum magnitude flag).
"""


def cleanup_column_prefix(df, inplace=False):
    """Method for shortening raw mosquito habitat mapper column names.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing raw mosquito habitat mapper data.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the cleaned up column prefixes. If `inplace=True` it returns None.
    """

    return replace_column_prefix(df, "mosquitohabitatmapper", "mhm", inplace=inplace)


def _entry_to_num(entry):
    try:
        if entry == "more than 100":
            return 101, 1, 1
        if pd.isna(entry):
            return -9999, 0, 0
        elif float(entry) > 100:
            return 101, min(math.floor(math.log10(float(entry) / 100)) + 1, 4), 0
        return float(entry), 0, 0
    except ValueError:
        return float(re.sub(r"-.*", "", entry)), 0, 1


def larvae_to_num(
    mhm_df,
    larvae_count_col="mhm_LarvaeCount",
    magnitude="mhm_LarvaeCountMagnitude",
    range_flag="mhm_LarvaeCountIsRangeFlag",
    inplace=False,
):
    """Converts the Larvae Count of the Mosquito Habitat Mapper Dataset from being stored as a string to integers.

    See [here](#converting-larvae-data-to-integers) for more information.

    Parameters
    ----------
    mhm_df : pd.DataFrame
        A DataFrame of Mosquito Habitat Mapper data that needs the larvae counts to be set to numbers
    larvae_count_col : str, default="mhm_LarvaeCount"
        The name of the column storing the larvae count. **Note**: The columns will be output in the format: `prefix_ColumnName` where `prefix` is all the characters that preceed the words `LarvaeCount` in the specified name.
    magnitude: str, default="mhm_LarvaeCountMagnitude"
        The name of the column which will store the generated LarvaeCountMagnitude output
    range_flag : str, default="mhm_LarvaeCountIsRangeFlag"
        The name of the column which will store the generated LarvaeCountIsRange flag
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the larvae count as integers. If `inplace=True` it returns None.
    """

    if not inplace:
        mhm_df = mhm_df.copy()
    # Preprocessing step to remove extremely erroneous values
    for i in mhm_df.index:
        count = mhm_df[larvae_count_col][i]
        if not pd.isna(count) and type(count) is str and "e+" in count:
            mhm_df.at[i, larvae_count_col] = "100000"

    larvae_conversion = np.vectorize(_entry_to_num)
    (
        mhm_df[larvae_count_col],
        mhm_df[magnitude],
        mhm_df[range_flag],
    ) = larvae_conversion(mhm_df[larvae_count_col].to_numpy())

    if not inplace:
        return mhm_df


def has_genus_flag(df, genus_col="mhm_Genus", bit_col="mhm_HasGenus", inplace=False):
    """
    Creates a bit flag: `mhm_HasGenus` where 1 denotes a recorded Genus and 0 denotes the contrary.

    Parameters
    ----------
    df : pd.DataFrame
        A mosquito habitat mapper DataFrame
    genus_col : str, default="mhm_Genus"
        The name of the column in the mosquito habitat mapper DataFrame that contains the genus records.
    bit_col : str, default="mhm_HasGenus"
        The name of the column which will store the generated HasGenus flag
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the HasGenus flag. If `inplace=True` it returns None.
    """
    if not inplace:
        df = df.copy()
    df[bit_col] = (~pd.isna(df[genus_col].to_numpy())).astype(int)

    if not inplace:
        return df


def infectious_genus_flag(
    df, genus_col="mhm_Genus", bit_col="mhm_IsGenusOfInterest", inplace=False
):
    """
    Creates a bit flag: `mhm_IsGenusOfInterest` where 1 denotes a Genus of a infectious mosquito and 0 denotes the contrary.

    Parameters
    ----------
    df : pd.DataFrame
        A mosquito habitat mapper DataFrame
    genus_col : str, default="mhm_Genus"
        The name of the column in the mosquito habitat mapper DataFrame that contains the genus records.
    bit_col : str, default="mhm_HasGenus"
        The name of the column which will store the generated IsGenusOfInterest flag
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the IsGenusOfInterest flag. If `inplace=True` it returns None.
    """
    if not inplace:
        df = df.copy()
    infectious_genus_flag = np.vectorize(
        lambda genus: genus in ["Aedes", "Anopheles", "Culex"]
    )
    df[bit_col] = infectious_genus_flag(df[genus_col].to_numpy()).astype(int)

    if not inplace:
        return df


def is_container_flag(
    df,
    watersource_col="mhm_WaterSourceType",
    bit_col="mhm_IsWaterSourceContainer",
    inplace=False,
):
    """
    Creates a bit flag: `mhm_IsWaterSourceContainer` where 1 denotes if a watersource is a container (e.g. ovitrap, pots, tires, etc.) and 0 denotes the contrary.

    Parameters
    ----------
    df : pd.DataFrame
        A mosquito habitat mapper DataFrame
    watersource_col : str, default="mhm_WaterSourceType"
        The name of the column in the mosquito habitat mapper DataFrame that contains the watersource type records.
    bit_col : str, default="mhm_IsWaterSourceContainer"
        The name of the column which will store the generated IsWaterSourceContainer flag
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the IsContainer flag. If `inplace=True` it returns None.
    """

    if not inplace:
        df = df.copy()

    mark_containers = np.vectorize(
        lambda container: not pd.isna(container) and "container" in container
    )
    df[bit_col] = mark_containers(df[watersource_col].to_numpy()).astype(int)

    if not inplace:
        return df


def has_watersource_flag(
    df, watersource_col="mhm_WaterSource", bit_col="mhm_HasWaterSource", inplace=False
):
    """
    Creates a bit flag: `mhm_HasWaterSource` where 1 denotes if there is a watersource and 0 denotes the contrary.

    Parameters
    ----------
    df : pd.DataFrame
        A mosquito habitat mapper DataFrame
    watersource_col : str, default="mhm_WaterSource"
        The name of the column in the mosquito habitat mapper DataFrame that contains the watersource records.
    bit_col : str, default="mhm_IsWaterSourceContainer"
        The name of the column which will store the generated HasWaterSource flag
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the HasWaterSource flag. If `inplace=True` it returns None.
    """

    if not inplace:
        df = df.copy()
    has_watersource = np.vectorize(lambda watersource: int(not pd.isna(watersource)))
    df[bit_col] = has_watersource(df[watersource_col].to_numpy())

    if not inplace:
        return df


def photo_bit_flags(
    df,
    watersource_photos="mhm_WaterSourcePhotoUrls",
    larvae_photos="mhm_LarvaFullBodyPhotoUrls",
    abdomen_photos="mhm_AbdomenCloseupPhotoUrls",
    photo_count="mhm_PhotoCount",
    rejected_count="mhm_RejectedCount",
    pending_count="mhm_PendingCount",
    photo_bit_binary="mhm_PhotoBitBinary",
    photo_bit_decimal="mhm_PhotoBitDecimal",
    inplace=False,
):
    """
    Creates the following flags:
    - `PhotoCount`: The number of valid photos per record.
    - `RejectedCount`: The number of photos that were rejected per record.
    - `PendingCount`: The number of photos that are pending approval per record.
    - `PhotoBitBinary`: A string that represents the presence of a photo in the order of watersource, larvae, and abdomen. For example, if the entry is `110`, that indicates that there is a water source photo and a larvae photo, but no abdomen photo.
    - `PhotoBitDecimal`: The numerical representation of the mhm_PhotoBitBinary string.

    Parameters
    ----------
    df : pd.DataFrame
        A mosquito habitat mapper DataFrame
    watersource_photos : str, default="mhm_WaterSourcePhotoUrls"
        The name of the column in the mosquito habitat mapper DataFrame that contains the watersource photo url records.
    larvae_photos : str, default="mhm_LarvaFullBodyPhotoUrls"
        The name of the column in the mosquito habitat mapper DataFrame that contains the larvae photo url records.
    abdomen_photos : str, default="mhm_AbdomenCloseupPhotoUrls"
        The name of the column in the mosquito habitat mapper DataFrame that contains the abdomen photo url records.
    photo_count : str, default="mhm_PhotoCount"
        The name of the column that will store the PhotoCount flag.
    rejected_count : str, default="mhm_RejectedCount"
        The name of the column that will store the RejectedCount flag.
    pending_count : str, default="mhm_PendingCount"
        The name of the column that will store the PendingCount flag.
    photo_bit_binary : str, default="mhm_PhotoBitBinary"
        The name of the column that will store the PhotoBitBinary flag.
    photo_bit_decimal : str, default="mhm_PhotoBitDecimal"
        The name of the column that will store the PhotoBitDecimal flag.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the photo flags. If `inplace=True` it returns None.
    """

    def pic_data(*args):
        pic_count = 0
        rejected_count = 0
        pending_count = 0
        valid_photo_bit_mask = ""

        # bit_power = len(args) - 1
        # For url string -- if we see ANY http, add 1
        # also count all valid photos, rejected photos,
        # If there are NO http then add 0, to empty photo field
        for url_string in args:
            if not pd.isna(url_string):
                if "http" not in url_string:
                    valid_photo_bit_mask += "0"
                else:
                    valid_photo_bit_mask += "1"

                pic_count += url_string.count("http")
                pending_count += url_string.count("pending")
                rejected_count += url_string.count("rejected")
            else:
                valid_photo_bit_mask += "0"

        return (
            pic_count,
            rejected_count,
            pending_count,
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
        df[photo_bit_binary],
        df[photo_bit_decimal],
    ) = get_photo_data(
        df[watersource_photos].to_numpy(),
        df[larvae_photos].to_numpy(),
        df[abdomen_photos].to_numpy(),
    )

    if not inplace:
        return df


def completion_score_flag(
    df,
    photo_bit_binary="mhm_PhotoBitBinary",
    has_genus="mhm_HasGenus",
    sub_completeness="mhm_SubCompletenessScore",
    completeness="mhm_CumulativeCompletenessScore",
    inplace=False,
):
    """
    Adds the following completness score flags:
    - `SubCompletenessScore`: The percentage of the watersource photos, larvae photos, abdomen photos, and genus columns that are filled out.
    - `CumulativeCompletenessScore`: The percentage of non null values out of all the columns.

    Parameters
    ----------
    df : pd.DataFrame
        A mosquito habitat mapper DataFrame with the [`PhotoBitDecimal`](#photo_bit_flags) and [`HasGenus`](#has_genus_flags) flags.
    photo_bit_binary: str, default="mhm_PhotoBitBinary"
        The name of the column in the mosquito habitat mapper DataFrame that contains the PhotoBitBinary flag.
    sub_completeness : str, default="mhm_HasGenus"
        The name of the column in the mosquito habitat mapper DataFrame that will contain the generated SubCompletenessScore flag.
    completeness : str, default="mhm_SubCompletenessScore"
        The name of the column in the mosquito habitat mapper DataFrame that will contain the generated CumulativeCompletenessScore flag.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame
        A DataFrame with completion score flags. If `inplace=True` it returns None.
    """

    def sum_bit_mask(bit_mask="0"):
        total = 0.0
        for char in bit_mask:
            total += int(char)
        return total

    if not inplace:
        df = df.copy()

    scores = {}
    scores["sub_score"] = []
    # Cummulative Completion Score
    scores["cumulative_score"] = round(df.count(axis=1) / len(df.columns), 2)
    # Sub-Score
    for index in df.index:
        bit_mask = df[photo_bit_binary][index]
        sub_score = df[has_genus][index] + sum_bit_mask(bit_mask=bit_mask)
        sub_score /= 4.0
        scores["sub_score"].append(sub_score)

    df[sub_completeness], df[completeness] = (
        scores["sub_score"],
        scores["cumulative_score"],
    )

    if not inplace:
        return df


def apply_cleanup(mhm_df):
    """Applies a full cleanup procedure to the mosquito habitat mapper data. Only returns a copy.
    It follows the following steps:
    - Removes Homogenous Columns
    - Renames Latitude and Longitudes
    - Cleans the Column Naming
    - Converts Larvae Count to Numbers
    - Rounds Columns
    - Standardizes Null Values

    Parameters
    ----------
    mhm_df : pd.DataFrame
        A DataFrame containing **raw** Mosquito Habitat Mapper Data from the API.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the cleaned up Mosquito Habitat Mapper Data
    """
    mhm_df = mhm_df.copy()

    rename_latlon_cols(mhm_df, inplace=True)
    cleanup_column_prefix(mhm_df, inplace=True)
    larvae_to_num(mhm_df, inplace=True)
    round_cols(mhm_df, inplace=True)
    standardize_null_vals(mhm_df, inplace=True)
    return mhm_df


def add_flags(mhm_df):
    """Adds the following flags to the Mosquito Habitat Mapper Data:
    - Has Genus
    - Is Infectious Genus/Genus of Interest
    - Is Container
    - Has WaterSource
    - Photo Bit Flags
    - Completion Score Flag

    This returns a copy of the original DataFrame with the flags added onto it.

    Parameters
    ----------
    mhm_df : pd.DataFrame
        A DataFrame containing cleaned up Mosquito Habitat Mapper Data ideally from the method.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the flagged Mosquito Habitat Mapper Data
    """
    mhm_df = mhm_df.copy()
    has_genus_flag(mhm_df, inplace=True)
    infectious_genus_flag(mhm_df, inplace=True)
    is_container_flag(mhm_df, inplace=True)
    has_watersource_flag(mhm_df, inplace=True)
    photo_bit_flags(mhm_df, inplace=True)
    completion_score_flag(mhm_df, inplace=True)
    return mhm_df


def plot_valid_entries(df, bit_col, entry_type):
    """
    Plots the number of entries with photos and the number of entries without photos

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing Mosquito Habitat Mapper Data with the PhotoBitDecimal Flag.
    """
    plt.figure()
    num_valid = len(df[df[bit_col] > 0])
    plt.title(f"Entries with {entry_type} vs No {entry_type}")
    plt.ylabel("Number of Entries")
    plt.bar(entry_type, num_valid, color="#e34a33")
    plt.bar(f"No {entry_type}", len(df) - num_valid, color="#fdcc8a")


def photo_subjects(mhm_df):
    """
    Plots the amount of photos for each photo area (Larvae, Abdomen, Watersource)

    Parameters
    ----------
    mhm_df : pd.DataFrame
        The DataFrame containing Mosquito Habitat Mapper Data with the PhotoBitDecimal Flag.
    """

    total_dict = {"Larvae Photos": 0, "Abdomen Photos": 0, "Watersource Photos": 0}

    for number in mhm_df["mhm_PhotoBitDecimal"]:
        total_dict["Watersource Photos"] += number & 4
        total_dict["Larvae Photos"] += number & 2
        total_dict["Abdomen Photos"] += number & 1

    for key in total_dict.keys():
        if total_dict[key] != 0:
            total_dict[key] = math.log10(total_dict[key])
        else:
            total_dict[key] = 0
    plt.figure(figsize=(10, 5))
    plt.title("Mosquito Habitat Mapper - Photo Subject Frequencies (Log Scale)")
    plt.xlabel("Photo Type")
    plt.ylabel("Frequency (Log Scale)")
    plt.bar(total_dict.keys(), total_dict.values(), color="lightblue")


def diagnostic_plots(mhm_df):
    """
    Generates (but doesn't display) diagnostic plots to gain insight into the current data.

    Plots:
    - Larvae Count Distribution (where a negative entry denotes null data)
    - Photo Subject Distribution
    - Number of valid photos vs no photos
    - Completeness Score Distribution
    - Subcompleteness Score Distribution

    Parameters
    ----------
    mhm_df : pd.DataFrame
        The DataFrame containing Flagged and Cleaned Mosquito Habitat Mapper Data.
    """
    plot_int_distribution(mhm_df, "mhm_LarvaeCount", "Larvae Count")
    photo_subjects(mhm_df)
    plot_freq_bar(mhm_df, "Mosquito Habitat Mapper", "mhm_Genus", "Genus Types")
    plot_valid_entries(mhm_df, "mhm_HasGenus", "Genus Classifications")
    plot_valid_entries(mhm_df, "mhm_PhotoBitDecimal", "Valid Photos")
    completeness_histogram(
        mhm_df,
        "Mosquito Habitat Mapper",
        "mhm_CumulativeCompletenessScore",
        "Cumulative Completeness",
    )
    completeness_histogram(
        mhm_df,
        "Mosquito Habitat Mapper",
        "mhm_SubCompletenessScore",
        "Sub Completeness",
    )


def qa_filter(
    mhm_df,
    has_genus=False,
    min_larvae_count=-9999,
    has_photos=False,
    is_container=False,
):
    """
    Can filter a cleaned and flagged mosquito habitat mapper DataFrame based on the following criteria:
    - `Has Genus`: If the entry has an identified genus
    - `Min Larvae Count` : Minimum larvae count needed for an entry
    - `Has Photos` : If the entry contains valid photo entries
    - `Is Container` : If the entry's watersource was a container

    Returns a copy of the DataFrame

    Parameters
    ----------
    has_genus : bool, default=False
        If True, only entries with an identified genus will be returned.
    min_larvae_count : int, default=-9999
        Only entries with a larvae count greater than or equal to this parameter will be included.
    has_photos : bool, default=False
        If True, only entries with recorded photos will be returned
    is_container : bool, default=False
        If True, only entries with containers will be returned

    Returns
    -------
    pd.DataFrame
        A DataFrame of the applied filters.
    """

    mhm_df = mhm_df[mhm_df["mhm_LarvaeCount"] >= min_larvae_count]

    if has_genus:
        mhm_df = mhm_df[mhm_df["mhm_HasGenus"] == 1]
    if has_photos:
        mhm_df = mhm_df[mhm_df["mhm_PhotoBitDecimal"] > 0]
    if is_container:
        mhm_df = mhm_df[mhm_df["mhm_IsWaterSourceContainer"] == 1]

    return mhm_df
