import os
import re
import warnings

import numpy as np
import pandas as pd
import requests


def get_globe_photo_id(url: str):
    """
    Gets the GLOBE Photo ID from a url

    Parameters
    ----------
    url : str
      A url to a GLOBE Observer Image
    """
    if pd.isna(url):
        return None
    else:
        match_obj = re.search(r"(?<=\d\d\d\d\/\d\d\/\d\d\/).*(?=\/)", url)
        if match_obj:
            photo_id = match_obj.group(0)
            return photo_id
    return None


def remove_bad_characters(filename: str):
    """
    Removes erroneous characters from filenames. This includes the `/` character as this is assuming that the filename is being passed, not a path that may include that symbol as part of a directory.

    Parameters
    ----------
    filename : str
      A possible filename.

    Returns
    -------
    str
        The filename without any erroneous characters
    """
    if pd.isna(filename):
        return None
    return re.sub(r"[<>:?\"/\\|*]", "", filename)


def download_photo(url: str, directory: str, filename: str):
    """
    Downloads a photo to a directory.

    Parameters
    ----------
    url : str
        The URL to the photo
    directory : str
        The directory that the photo should be saved in
    filename : str
        The name of the photo
    """
    if any(pd.isna(x) for x in [url, directory, filename]):
        msg = f"Either url ({url}), directory ({directory}), or filename ({filename}) was None."
        warnings.warn(msg)
    else:
        downloaded_obj = requests.get(url, allow_redirects=True)
        filename = remove_bad_characters(filename)
        out_path = os.path.join(directory, filename)
        with open(out_path, "wb") as file:
            file.write(downloaded_obj.content)


def download_all_photos(targets):
    """
    Downloads all photos given a list of targets which are tuples containing the url, directory, and filename.

    Parameters
    ----------
    targets : list of tuple of str
        Contains tuples that store the url, directory, and filename of the desired photos to be downloaded in that order.
    """
    expectedNumParams = 3
    if pd.isna(targets):
        warnings.warn("Targets was none")
    else:
        for target in targets:
            if (type(target) is tuple) and len(target) == expectedNumParams:
                download_photo(*target)
            else:
                warnings.warn(f"Target incorrectly formatted: {target}")


def _format_param_name(name: str):
    if pd.isna(name):
        return None
    return (
        "".join(s.capitalize() + " " for s in name.split("_"))
        .replace("Photo", "")
        .strip()
    )


# Constructs Photo Name using given included fields and additional information
def _build_photo_name(
    protocol, photo_id, name_fields, include_in_name=[], additional_name_stem=""
):
    valid_protocols = ["lc_", "mhm_"]
    if not protocol or protocol not in valid_protocols:
        warnings.warn("Invalid protocol")
        return None
    name = protocol
    if additional_name_stem and additional_name_stem != "":
        name += f"{additional_name_stem}_"

    if include_in_name:
        for field in list(include_in_name):
            if field in set(name_fields):
                name += f"{name_fields[field]}_"

    name += f"{photo_id}.png"
    name = remove_bad_characters(name)
    return name


def _get_mosquito_classification(genus, species):
    classification = genus
    if pd.isna(classification):
        classification = "None"
    elif not pd.isna(species):
        classification = f"{classification} {species}"
    return classification


def _warn_num_invalid_photos(num_invalid_photos: dict):
    if sum(num_invalid_photos.values()) > 0:
        msg = f"Skipped {sum(num_invalid_photos.values())} invalid photos: "
        msg += str(num_invalid_photos)
        warnings.warn(msg)


def get_mhm_download_targets(
    mhm_df,
    directory,
    latitude_col="mhm_Latitude",
    longitude_col="mhm_Longitude",
    watersource_col="mhm_WaterSource",
    date_col="mhm_measuredDate",
    id_col="mhm_MosquitoHabitatMapperId",
    genus_col="mhm_Genus",
    species_col="mhm_Species",
    larvae_photo="mhm_LarvaFullBodyPhotoUrls",
    watersource_photo="mhm_WaterSourcePhotoUrls",
    abdomen_photo="mhm_AbdomenCloseupPhotoUrls",
    include_in_name=[],
    additional_name_stem="",
):
    """
    Generates mosquito habitat mapper targets to download

    Parameters
    ----------
    mhm_df : pd.DataFrame
        Mosquito Habitat Mapper Data
    directory : str
        The directory to save the photos
    latitude_col : str, default="mhm_Latitude"
        The column name of the column that contains the Latitude
    longitude_col : str, default="mhm_Longitude"
        The column name of the column that contains the Longitude
    watersource_col : str, default = "mhm_WaterSource"
        The column name of the column that contains the watersource
    date_col : str, default = "mhm_measuredDate"
        The column name of the column that contains the measured date
    id_col : str, default = "mhm_MosquitoHabitatMapperId"
        The column name of the column that contains the mosquito habitat mapper id
    genus_col : str, default = "mhm_Genus"
        The column name of the column that contains the genus
    species_col : str, default = "mhm_Species"
        The column name of the column that contains the species
    larvae_photo : str, default = "mhm_LarvaFullBodyPhotoUrls"
        The column name of the column that contains the larvae photo urls. If not specified, the larvae photos will not be included.
    watersource_photo : str, default = "mhm_WaterSourcePhotoUrls"
        The column name of the column that contains the watersource photo urls. If not specified, the larvae photos will not be included.
    abdomen_photo : str, default = "mhm_AbdomenCloseupPhotoUrls"
        The column name of the column that contains the abdomen photo urls. If not specified, the larvae photos will not be included.
    include_in_name : list of str, default=[]
        A list of column names to include into the downloaded photo names. The order of items in this list is maintained in the outputted name
        Accepted Included Names include:
            * `url_type` -- Type of photo (e.g. Watersource, Larvae, Abdomen)
            * `watersource` -- Watersource for the observed mosquito habitat
            * `latitude` -- GPS Latitude Coordinate (rounded to 5 decimal places)
            * `longitude` -- GPS Longitude Coordinate (rounded to 5 decimal places)
            * `date_str` -- Date Range expressed as a String
            * `mhm_id` -- Unique ID for a MHM observation
            * `classification` -- Mosquito classification (or `"None"` if no classification available)
    additional_name_stem : str, default=""
        Additional custom information the user can add to the name.

    Returns
    -------
    set of tuple of str
        Contains the (url, directory, and filename) for each desired mosquito habitat mapper photo
    """
    arguments = locals()
    targets = set()
    num_invalid_photos = {
        "invalid_URL": 0,
        "rejected": 0,
        "pending": 0,
        "bad_photo_id": 0,
    }

    def get_photo_args(
        url_entry,
        url_type,
        latitude,
        longitude,
        watersource,
        date,
        mhm_id,
        genus,
        species,
    ):
        if pd.isna(url_entry):
            return

        urls = url_entry.split(";")
        date_str = pd.to_datetime(str(date)).strftime("%Y-%m-%d")

        for url in urls:
            if not pd.isna(url) and "https" in url:
                photo_id = get_globe_photo_id(url)

                name_fields = {
                    "url_type": url_type,
                    "watersource": watersource,
                    "latitude": round(latitude, 5),
                    "longitude": round(longitude, 5),
                    "date_str": date_str,
                    "mhm_id": mhm_id,
                    "classification": _get_mosquito_classification(genus, species),
                }

                # Checks photo_id is valid
                if not pd.isna(photo_id) and int(photo_id) >= 0:
                    protocol = "mhm_"
                    name = _build_photo_name(
                        protocol,
                        photo_id,
                        name_fields,
                        include_in_name,
                        additional_name_stem,
                    )
                    targets.add((url, directory, name))
                else:
                    num_invalid_photos["bad_photo_id"] += 1
            elif not pd.isna(url) and "rejected" in url:
                num_invalid_photos["rejected"] += 1
            elif not pd.isna(url) and "pending" in url:
                num_invalid_photos["pending"] += 1
            else:
                num_invalid_photos["invalid_URL"] += 1

    photo_locations = {k: v for k, v in arguments.items() if "photo" in k}
    for param_name, column_name in photo_locations.items():
        if column_name:
            get_mosquito_args = np.vectorize(get_photo_args)
            get_mosquito_args(
                mhm_df[column_name].to_numpy(),
                _format_param_name(param_name),
                mhm_df[latitude_col].to_numpy(),
                mhm_df[longitude_col].to_numpy(),
                mhm_df[watersource_col].to_numpy(),
                mhm_df[date_col],
                mhm_df[id_col].to_numpy(),
                mhm_df[genus_col].to_numpy(),
                mhm_df[species_col].to_numpy() if species_col else "",
            )
    _warn_num_invalid_photos(num_invalid_photos)
    return targets


def download_mhm_photos(
    mhm_df,
    directory,
    latitude_col="mhm_Latitude",
    longitude_col="mhm_Longitude",
    watersource_col="mhm_WaterSource",
    date_col="mhm_measuredDate",
    id_col="mhm_MosquitoHabitatMapperId",
    genus_col="mhm_Genus",
    species_col="mhm_Species",
    larvae_photo="mhm_LarvaFullBodyPhotoUrls",
    watersource_photo="mhm_WaterSourcePhotoUrls",
    abdomen_photo="mhm_AbdomenCloseupPhotoUrls",
    include_in_name=[],
    additional_name_stem="",
):
    """
    Downloads mosquito habitat mapper photos

    Parameters
    ----------
    mhm_df : pd.DataFrame
        Mosquito Habitat Mapper Data
    directory : str
        The directory to save the photos
    latitude_col : str, default="mhm_Latitude"
        The column name of the column that contains the Latitude
    longitude_col : str, default="mhm_Longitude"
        The column name of the column that contains the Longitude
    watersource_col : str, default = "mhm_WaterSource"
        The column name of the column that contains the watersource
    date_col : str, default = "mhm_measuredDate"
        The column name of the column that contains the measured date
    id_col : str, default = "mhm_MosquitoHabitatMapperId"
        The column name of the column that contains the mosquito habitat mapper id
    genus_col : str, default = "mhm_Genus"
        The column name of the column that contains the genus
    species_col : str, default = "mhm_Species"
        The column name of the column that contains the species
    larvae_photo : str, default = "mhm_LarvaFullBodyPhotoUrls"
        The column name of the column that contains the larvae photo urls. If not specified, the larvae photos will not be included.
    watersource_photo : str, default = "mhm_WaterSourcePhotoUrls"
        The column name of the column that contains the watersource photo urls. If not specified, the larvae photos will not be included.
    abdomen_photo : str, default = "mhm_AbdomenCloseupPhotoUrls"
        The column name of the column that contains the abdomen photo urls. If not specified, the larvae photos will not be included.
    include_in_name : list of str, default=[]
        A list of column names to include into the downloaded photo names. The order of items in this list is maintained in the outputted name list of column names to include into the downloaded photo names
        Accepted Included Names include:
            * `url_type` -- Type of photo (e.g. Watersource, Larvae, Abdomen)
            * `watersource` -- Watersource for the observed mosquito habitat
            * `latitude` -- GPS Latitude Coordinate (rounded to 5 decimal places)
            * `longitude` -- GPS Longitude Coordinate (rounded to 5 decimal places)
            * `date_str` -- Date Range expressed as a String
            * `mhm_id` -- Unique ID for a MHM observation
            * `classification` -- Mosquito classification (or `"None"` if no classification available)
    additional_name_stem : str, default=""
        Additional custom information the user can add to the name.

    Returns
    -------
    set of tuple of str
        Contains the (url, directory, and filename) for each desired mosquito habitat mapper photo
    """
    if not os.path.exists(directory):
        os.mkdir(directory)
    targets = get_mhm_download_targets(**locals())
    download_all_photos(targets)
    return targets


def get_lc_download_targets(
    lc_df,
    directory,
    latitude_col="lc_Latitude",
    longitude_col="lc_Longitude",
    date_col="lc_measuredDate",
    id_col="lc_LandCoverId",
    up_photo="lc_UpwardPhotoUrl",
    down_photo="lc_DownwardPhotoUrl",
    north_photo="lc_NorthPhotoUrl",
    south_photo="lc_SouthPhotoUrl",
    east_photo="lc_EastPhotoUrl",
    west_photo="lc_WestPhotoUrl",
    include_in_name=[],
    additional_name_stem="",
):
    """
    Generates landcover targets to download

    Parameters
    ----------
    lc_df : pd.DataFrame
        Cleaned and Flagged Landcover Data
    directory : str
        The directory to save the photos
    latitude_col : str, default="lc_Latitude"
        The column of the column that contains the Latitude
    longitude_col : str, default="lc_Longitude"
        The column of the column that contains the Longitude
    date_col : str, default="lc_measuredDate"
        The column name of the column that contains the measured date
    id_col : str, default="lc_LandCoverId"
        The column name of the column that contains the landcover id
    up_photo : str, default = "lc_UpwardPhotoUrl"
        The column name of the column that contains the upward photo urls. If not specified, these photos will not be included.
    down_photo : str, default = "lc_DownwardPhotoUrl"
        The column name of the column that contains the downward photo urls. If not specified, these photos will not be included.
    north_photo : str, default = "lc_NorthPhotoUrl"
        The column name of the column that contains the north photo urls. If not specified, these photos will not be included.
    south_photo : str, default = "lc_SouthPhotoUrl"
        The column name of the column that contains the south photo urls. If not specified, these photos will not be included.
    east_photo : str, default = "lc_EastPhotoUrl"
        The column name of the column that contains the east photo urls. If not specified, these photos will not be included.
    west_photo : str, default = "lc_WestPhotoUrl"
        The column name of the column that contains the west photo urls. If not specified, these photos will not be included.
    include_in_name : list of str, default=[]
        A list of column names to include into the downloaded photo names. The order of items in this list is maintained in the outputted name
        Accepted Included Names include:
            * `direction` -- Direction where the photo was taken (e.g. North, South, East, West, Up, Down)
            * `latitude` -- GPS Latitude Coordinate (rounded to 5 decimal places)
            * `longitude` -- GPS Longitude Coordinate (rounded to 5 decimal places)
            * `date_str` -- Date Range expressed as a String
            * `lc_id` -- Unique ID for a LC observation
    additional_name_stem : str, default=""
        Additional custom information the user can add to the name.

    Returns
    -------
    set of tuple of str
        Contains the (url, directory, and filename) for each desired land cover photo
    """
    arguments = locals()
    targets = set()
    num_invalid_photos = {
        "invalid_URL": 0,
        "rejected": 0,
        "pending": 0,
        "bad_photo_id": 0,
    }

    def get_photo_args(url, latitude, longitude, direction, date, lc_id):
        if not pd.isna(url) and "https" in url:
            date_str = pd.to_datetime(str(date)).strftime("%Y-%m-%d")
            photo_id = get_globe_photo_id(url)

            name_fields = {
                "direction": direction,
                "latitude": round(latitude, 5),
                "longitude": round(longitude, 5),
                "date_str": date_str,
                "lc_id": lc_id,
            }

            if not pd.isna(photo_id) and int(photo_id) >= 0:
                protocol = "lc_"
                name = _build_photo_name(
                    protocol,
                    photo_id,
                    name_fields,
                    include_in_name,
                    additional_name_stem,
                )
                targets.add((url, directory, name))
            else:
                num_invalid_photos["bad_photo_id"] += 1
        elif not pd.isna(url) and "rejected" in url:
            num_invalid_photos["rejected"] += 1
        elif not pd.isna(url) and "pending" in url:
            num_invalid_photos["pending"] += 1
        else:
            num_invalid_photos["invalid_URL"] += 1

    photo_locations = {k: v for k, v in arguments.items() if "photo" in k}
    for param_name, column_name in photo_locations.items():
        if column_name:
            get_lc_photo_args = np.vectorize(get_photo_args)
            get_lc_photo_args(
                lc_df[column_name].to_numpy(),
                lc_df[latitude_col].to_numpy(),
                lc_df[longitude_col].to_numpy(),
                _format_param_name(param_name),
                lc_df[date_col],
                lc_df[id_col].to_numpy(),
            )
    _warn_num_invalid_photos(num_invalid_photos)
    return targets


def download_lc_photos(
    lc_df,
    directory,
    latitude_col="lc_Latitude",
    longitude_col="lc_Longitude",
    date_col="lc_measuredDate",
    id_col="lc_LandCoverId",
    up_photo="lc_UpwardPhotoUrl",
    down_photo="lc_DownwardPhotoUrl",
    north_photo="lc_NorthPhotoUrl",
    south_photo="lc_SouthPhotoUrl",
    east_photo="lc_EastPhotoUrl",
    west_photo="lc_WestPhotoUrl",
    include_in_name=[],
    additional_name_stem="",
):
    """
    Downloads Landcover photos for landcover data.

    Parameters
    ----------
    lc_df : pd.DataFrame
        Cleaned and Flagged Landcover Data
    directory : str
        The directory to save the photos
    latitude_col : str, default="lc_Latitude"
        The column of the column that contains the Latitude
    longitude_col : str, default="lc_Longitude"
        The column of the column that contains the Longitude
    date_col : str, default="lc_measuredDate"
        The column name of the column that contains the measured date
    id_col : str, default="lc_LandCoverId"
        The column name of the column that contains the landcover id
    up_photo : str, default = "lc_UpwardPhotoUrl"
        The column name of the column that contains the upward photo urls. If not specified, these photos will not be included.
    down_photo : str, default = "lc_DownwardPhotoUrl"
        The column name of the column that contains the downward photo urls. If not specified, these photos will not be included.
    north_photo : str, default = "lc_NorthPhotoUrl"
        The column name of the column that contains the north photo urls. If not specified, these photos will not be included.
    south_photo : str, default = "lc_SouthPhotoUrl"
        The column name of the column that contains the south photo urls. If not specified, these photos will not be included.
    east_photo : str, default = "lc_EastPhotoUrl"
        The column name of the column that contains the east photo urls. If not specified, these photos will not be included.
    west_photo : str, default = "lc_WestPhotoUrl"
        The column name of the column that contains the west photo urls. If not specified, these photos will not be included.
    include_in_name : list of str, default=[]
        A list of column names to include into the downloaded photo names. The order of items in this list is maintained in the outputted name
        Accepted Included Names include:
            * `direction` -- Direction where the photo was taken (e.g. North, South, East, West, Up, Down)
            * `latitude` -- GPS Latitude Coordinate (rounded to 5 decimal places)
            * `longitude` -- GPS Longitude Coordinate (rounded to 5 decimal places)
            * `date_str` -- Date Range expressed as a String
            * `lc_id` -- Unique ID for a LC observation
    additional_name_stem : str, default=""
        Additional custom information the user can add to the name.

    Returns
    -------
    set of tuple of str
        Contains the (url, directory, and filename) for each desired land cover photo
    """
    if not os.path.exists(directory):
        os.mkdir(directory)

    targets = get_lc_download_targets(**locals())
    download_all_photos(targets)
    return targets
