"""
Utility methods for handling input and output files from blocks and their
respective metadata in `data.json`.
"""
from typing import Any, Tuple, Optional, Union
from pathlib import Path
from geojson import Feature

DATA_PATH = "up42.data_path"


def set_data_path(feature: Feature, data_path: Any) -> Feature:
    """Set path to file in a output feature. Key for data path is always `up42.data_path`.

    Parameters:
        feature: The output feature.
        data_path: Relative path to the output file from the main working folder
            (i.e. `output.tif` is `/tmp/output/output.tif`).

    Returns:
        Output feature with the data path set.
    """
    feature["properties"][DATA_PATH] = data_path
    return feature


def get_data_path(feature: Feature) -> Any:
    """Get path to file in a input feature. Key for data path is always `up42.data_path`.

    Parameters:
        feature: The input feature.

    Returns:
        Relative path to the input file from the main working folder
        (i.e. `input.tif` is `/tmp/input/input.tif`).
    """
    return feature["properties"][DATA_PATH]


def get_output_filename_and_path(
    input_file_name: Union[str, Path],
    postfix: str = "",
    mkdir: bool = True,
    out_path_dir: Path = Path("/tmp/output/"),
    out_file_extension: str = "",
) -> Tuple[str, Path]:
    """
    Utility to generate both output file name and also output file path. Will
    create parent(s) directory(ies) of output file by default.

    Parameters:
        input_file_name :
            File name you can get with `get_data_path` method.
        postfix :
            Additional string to add to the end of the file name before the file suffix or
            format. By default it adds "_" plus postfix.
        mkdir :
            If set to true (default) will create parents of output file path.
        out_path_dir :
            Output path parents. By defaults /tmp/output.
        out_file_extension:
            Output file extension or suffix. Will use input file extension if not explicitly
            set (i.e. .tiff).

    Returns:
        Tuple with str of output file name and output file path that can be passed
        to process to save as output file.
    """
    input_file_name = Path(input_file_name)  # type: ignore
    if out_file_extension == "":
        out_file_extension = input_file_name.suffix
    if postfix == "":
        output_file_name = input_file_name.parent / Path(
            input_file_name.stem + out_file_extension
        )
    else:
        output_file_name = input_file_name.parent / Path(
            input_file_name.stem + "_" + postfix + out_file_extension
        )
    output_file_path = out_path_dir / output_file_name
    if mkdir:
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
    return str(output_file_name), output_file_path


def get_in_out_feature_names_and_paths(
    in_feature: Feature,
    postfix: Optional[str] = None,
    suffix: Optional[str] = None,
) -> Tuple[str, str, Path, Path]:
    """
    Utility to generate the input and output feature names and file paths. Will create
    parent directory(ies) of output file by default. Optionally augments the output filename
    with a postfix.

    Parameters:
        in_feature : A Feature of a GeoJSON FeatureCollection describing all input datasets
        postfix : Additional string to add to the end of the file name before
            the file suffix, adds "_" plus postfix. E.g. "lvl3".
        suffix: Suffix replacement, requires dot e.g. ".tif".

    Returns:
        Tuple with str of in- & output feature names and in- & output file paths.
    """
    in_feature_name = in_feature["properties"][DATA_PATH]
    in_feature_path = Path("/tmp/input") / in_feature_name

    if postfix is None:
        out_feature_name = Path(in_feature_name)
    else:
        in_feature_name = Path(in_feature_name)
        out_feature_name = in_feature_name.with_name(
            in_feature_name.stem + "_" + postfix + in_feature_name.suffix
        )
    if suffix is not None:
        out_feature_name = out_feature_name.with_suffix(suffix)

    out_feature_path = Path("/tmp/output") / out_feature_name
    out_feature_path.parent.mkdir(parents=True, exist_ok=True)

    return (
        str(in_feature_name),
        str(out_feature_name),
        in_feature_path,
        out_feature_path,
    )
