# flake8: noqa

from go_utils.download import get_api_data

__docformat__ = "restructuredtext"

__doc__ = """
go_utils contains utilities for interfacing with the GLOBE Observer datasets, primarily the Mosquito Habitat Mapper and Landcover.

Main Features
-------------
Here are the major utilities provided by the package:

- Easy downloading of the GLOBE Observer datasets as Pandas DataFrames
- Utilities for cleaning up Mosquito Habitat Mapper and Landcover Datasets
- CLI Scripts for downloading data and photos for the Mosquito Habitat Mapper and Landcover Protocols.

Example Notebooks
-----------------
[Example Notebooks](https://github.com/IGES-Geospatial/globe-observer-utils/tree/main/notebooks) have been made to show basic examples and applications of this library.

CLI Script Documentation
-----------

The CLI Scripts are intended to provide fast and accessible ways of collecting cleaned GLOBE Observer data from the commandline.

## Getting GLOBE Data CSVs
There are two commands that can be used to get data from Mosquito Habitat Mapper and Land Cover, respectively.
For Mosquito Habitat Mapper, there is `mhm-data-download` and for Land Cover, there is `lc-data-download`.

For each of these commands, there are several flags that can be specified to narrow down the data:
### General Flags

#### Output Path
You can use `--out` or `-o` followed by a file path to specify the output path of the download. If this is not specified, the script will generate diagnostic plots for you to get insight into the data that you would be downloading.

#### Start and End Dates
You can use `--start` or `-s` followed by a date in YYYY-MM-DD form to specify the start date. Similarly, you can use `--end` or `-e` to specify the end date.

#### Countries
You can use `--countries` or `-co` followed by a list of countries separated by commas to specify a download of specific country data. For example `-co "Brazil, Argentina"` would only download data from Brazil and Argentina.

#### Regions
You can use `--regions` or `-r` followed by a list of regions separated by commas to specify a download of specific GLOBE region data. For example `-r "North America"` would download data from North America. See the region dictionary to see the countries that comprise each GLOBE Region.

#### Bounding Box
You can use `--box` or `-b` followed by the coordinates of your bounding box in this format: `min latitude, min longitude, max latitude, max longitude`

### Mosquito Habitat Mapper Flags

#### Genus
You can use `--hasgenus` or `-hg` to only get data that has an identified genus.

#### Container
You can use `--iscontainer` or `-ic` to only get data which has a container as a watersource.

#### Photo
You can use `--hasphotos` or `-hp` to only get data which has recorded photo entries.

#### Minimum Larvae Count
You can use `--minlarvae` or `-ml` to only get data which has a certain amount of larvae.

#### Example
The command:
```py
mhm-download -s "2021-05-01" -e "2021-05-31" -hg -o MHM_Regular_Test.csv
```

Would download all mosquito mapper data with an identified genus during May 1st, 2021 to May 31st, 2021 into a `MHM_Regular_Test.csv` file.
### Land Cover Flags

#### Has a Classification
You can use `--hasclassification` or `-hc` to only get data which has atleast one Land Cover Classification.

#### Has Photo
You can use `--hasphoto` or `-hp` to only get data which has atleast one Photo entry.

#### Has All Classifications
You can use `--hasallclassifications` or `-hac` to only get data which has all classifications filled out.

#### Has All Photos
You can use `--hasallphotos` or `-hap` to only get data which has all photos filled out.

#### Example
The command:
```py
lc-download -s "2021-05-01" -e "2021-05-31" -hap -o LC_Regular_Test.csv
```

Would download all landcover data with fully filled out photo observations during May 1st, 2021 to May 31st, 2021 into a `LC_Regular_Test.csv` file.

## Downloading Photos
There are two commands that can be used to get photos for cleaned Mosquito Habitat Mapper and Land Cover CSV files, respectively.
For Mosquito Habitat Mapper, there is `mhm-photo-download` and for Land Cover, there is `lc-photo-download`.

### General Command
In order for the photo download scripts to work, you must specify an input path and output path.
For example, `mhm_photo_download "input csv path" "output directory"` will take the Mosquito Habitat Mapper data stored in the input CSV and download the photos to the output directory. If the output directory doesn't exist, it will be created.

#### All Flag
You can use the `--all` or `-a` to set all the following flags.

#### Custom Photo Naming Flags
* Use `--name_additional` or `-add` to add custom additional information to the photo names.
* Use `--nargs_include` or `-in` to include a field from the default photo name. Can include any of the following:
    * For **mosquito_habitat_mapper** -- Accepted Included Names include:
        * `url_type` -- Type of photo (e.g. Watersource, Larvae, Abdomen)
        * `watersource` -- Watersource for the observed mosquito habitat
        * `latitude` -- GPS Latitude Coordinate (rounded to 5 decimal places)
        * `longitude` -- GPS Longitude Coordinate (rounded to 5 decimal places)
        * `date_str` -- Date Range expressed as a String
        * `mhm_id` -- Unique ID for a MHM observation
        * `classification` -- Mosquito classification (or `"None"` if no classification available)
    * For **land_cover** -- Accepted Included Names include:
        * `direction` -- Direction where the photo was taken (e.g. North, South, East, West, Up, Down)
        * `latitude` -- GPS Latitude Coordinate (rounded to 5 decimal places)
        * `longitude` -- GPS Longitude Coordinate (rounded to 5 decimal places)
        * `date_str` -- Date Range expressed as a String
        * `lc_id` -- Unique ID for a LC observation

### Mosquito Specifics

#### Larvae Photos
You can use `--larvae` or `-l` to specify the download of larvae photos.

#### Watersource Photos
You can use `--watersource` or  `-w` to specify the download of watersource photos.

#### Abdomen Photos
You can use `--abdomen` or "-ab" to specify the download of abdomen photos.

#### Example
The command
```py
mhm-photo-download mhm_sample.csv mhm_outdir
```
Would download all mosquito mapper photos in the `mhm_sample.csv` file to a directory named `mhm_outdir`
### Landcover Specifics

#### Up Photos
You can use `--up` or `-u` to specify the download of upward photos.

#### Down Photos
You can use `--down` or `-d` to specify the download of downward photos.

#### North Photos
You can use `--north` or `-n` to specify the download of northward photos.

#### South Photos
You can use `--south` or `-s` to specify the download of southward photos.

#### East Photos
You can use `--east` or `-e` to specify the download of eastward photos.

#### West Photos
You can use `--west` or `-w` to specify the download of westward photos.

#### Example
The command:
```py
lc-photo-download lc_sample.csv lc_outdir -a
```
Would download all landcover photos in the `lc_sample.csv` file to a directory named `lc_outdir`
"""
