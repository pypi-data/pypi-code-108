from captur_ml_sdk.utils.gcp_functions import (
    get_requested_model_id, check_file_exists, get_model_type_from_gcp
)

from captur_ml_sdk.dtypes.exceptions import (
    ModelNotFoundError, VersionNotFoundError, ModelHasNoLiveVersionsError
)


def check_images_or_imagefile_has_data(cls, values):
    if not values.get('images') and not values.get('imagesfile'):
        raise ValueError(
            "At least one of 'images' and 'imagesfile' must be set."
        )

    return values


def check_model_exists(cls, values):
    name = values.get("name")
    version = values.get("version")
    try:
        model_id = get_requested_model_id(name, version)
        values["version"] = model_id
    except (ModelNotFoundError, VersionNotFoundError, ModelHasNoLiveVersionsError) as e:
        raise TypeError(str(e))

    return values


def fetch_model_type(cls, values):
    name = values.get("name")
    try:
        model_type = get_model_type_from_gcp(name)
        values["type"] = model_type
    except ModelNotFoundError as e:
        raise TypeError(str(e))
    return values


def ensure_file_exists(cls, v):
    if v:
        if not check_file_exists(v):
            raise ValueError(
                f"File: {v} has not been found."
            )
    return v


def check_images_or_imagesfile_is_included(cls, values):
    images = values.get("images")
    imagesfile = values.get("imagesfile")

    if not imagesfile and not images:
        raise ValueError(
            "One of predict:data.imagesfile or predict:data.images must be included"
        )
    return values


def enforce_mutual_exclusivity_between_images_and_imagesfile(cls, values):
    images = values.get("images")
    imagesfile = values.get("imagesfile")

    if images and imagesfile:
        raise ValueError(
            "Only one of predict:data.images or predict:data.imagesfile can be used"
        )
    return values
