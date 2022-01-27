"""Implement kaibu-utils."""
import io

import numpy as np
from geojson import Feature, FeatureCollection
from geojson import Polygon as geojson_polygon
from geojson import dumps
from PIL import Image, ImageDraw
from skimage import draw as skimage_draw
from skimage import measure, morphology
from scipy import ndimage as ndi

try:
    # scikit-image >= 0.19
    from skimage.segmentation import watershed
except ImportError:
    from skimage.morphology import watershed

from skimage.morphology import remove_small_objects

try:
    import pyodide

    is_pyodide = True
except ImportError:
    is_pyodide = False


def load_features(features, image_size):
    # Loop over list and create simple dictionary & get size of annotations
    annot_dict = {}

    skipped = []

    for feat_idx, feat in enumerate(features):
        if feat["geometry"]["type"] not in ["Polygon", "LineString"]:
            skipped.append(feat["geometry"]["type"])
            continue

        # skip empty roi
        if len(feat["geometry"]["coordinates"][0]) <= 0:
            continue

        key_annot = "annot_" + str(feat_idx)
        annot_dict[key_annot] = {}
        annot_dict[key_annot]["type"] = feat["geometry"]["type"]
        annot_dict[key_annot]["pos"] = np.squeeze(
            np.asarray(feat["geometry"]["coordinates"])
        )
        annot_dict[key_annot]["properties"] = feat["properties"]

    # print("Skipped geometry type(s):", skipped)
    return annot_dict, image_size


def generate_binary_masks(
    annot_dict,
    image_size=(2048, 2048),
    erose_size=5,
    obj_size_rem=500,
    save_indiv=False,
):
    """
    Create masks from annotation dictionary

    Args:
        annot_dict (dictionary): dictionary with annotations

    Returns:
        mask_dict (dictionary): dictionary with masks
    """

    # Get dimensions of image and created masks of same size
    # This we need to save somewhere (e.g. as part of the geojson file?)

    # Filled masks and edge mask for polygons
    mask_fill = np.zeros(image_size, dtype=np.uint8)
    mask_edge = np.zeros(image_size, dtype=np.uint8)
    mask_labels = np.zeros(image_size, dtype=np.uint16)

    rr_all = []
    cc_all = []

    if save_indiv is True:
        mask_edge_indiv = np.zeros(
            (image_size[0], image_size[1], len(annot_dict)), dtype=np.bool
        )
        mask_fill_indiv = np.zeros(
            (image_size[0], image_size[1], len(annot_dict)), dtype=np.bool
        )

    # Image used to draw lines - for edge mask for freelines
    im_freeline = Image.new("1", (image_size[1], image_size[0]), color=0)
    draw = ImageDraw.Draw(im_freeline)

    # Loop over all roi
    i_roi = 0
    for roi_key, roi in annot_dict.items():
        roi_pos = roi["pos"]

        # Check region type

        # freeline - line
        if roi["type"] == "freeline" or roi["type"] == "LineString":

            # Loop over all pairs of points to draw the line

            for ind in range(roi_pos.shape[0] - 1):
                line_pos = (
                    roi_pos[ind, 1],
                    roi_pos[ind, 0],
                    roi_pos[ind + 1, 1],
                    roi_pos[ind + 1, 0],
                )
                draw.line(line_pos, fill=1, width=erose_size)

        # freehand - polygon
        elif (
            roi["type"] == "freehand"
            or roi["type"] == "polygon"
            or roi["type"] == "polyline"
            or roi["type"] == "Polygon"
        ):

            # Draw polygon
            rr, cc = skimage_draw.polygon(
                [image_size[0] - r for r in roi_pos[:, 1]], roi_pos[:, 0]
            )

            # Make sure it's not outside
            rr[rr < 0] = 0
            rr[rr > image_size[0] - 1] = image_size[0] - 1

            cc[cc < 0] = 0
            cc[cc > image_size[1] - 1] = image_size[1] - 1

            # Test if this region has already been added
            if any(np.array_equal(rr, rr_test) for rr_test in rr_all) and any(
                np.array_equal(cc, cc_test) for cc_test in cc_all
            ):
                # print('Region #{} has already been used'.format(i +
                # 1))
                continue

            rr_all.append(rr)
            cc_all.append(cc)

            # Generate mask
            mask_fill_roi = np.zeros(image_size, dtype=np.uint8)
            mask_fill_roi[rr, cc] = 1

            # Erode to get cell edge - both arrays are boolean to be used as
            # index arrays later
            mask_fill_roi_erode = morphology.binary_erosion(
                mask_fill_roi, np.ones((erose_size, erose_size))
            )
            mask_edge_roi = (
                mask_fill_roi.astype("int") - mask_fill_roi_erode.astype("int")
            ).astype("bool")

            # Save array for mask and edge
            mask_fill[mask_fill_roi > 0] = 1
            mask_edge[mask_edge_roi] = 1
            mask_labels[mask_fill_roi > 0] = i_roi + 1

            if save_indiv is True:
                mask_edge_indiv[:, :, i_roi] = mask_edge_roi.astype("bool")
                mask_fill_indiv[:, :, i_roi] = mask_fill_roi_erode.astype("bool")

            i_roi = i_roi + 1

        else:
            roi_type = roi["type"]
            raise NotImplementedError(
                f'Mask for roi type "{roi_type}" can not be created'
            )

    del draw

    # Convert mask from free-lines to numpy array
    mask_edge_freeline = np.asarray(im_freeline)
    mask_edge_freeline = mask_edge_freeline.astype("bool")

    # Post-processing of fill and edge mask - if defined
    mask_dict = {}
    if np.any(mask_fill):

        # (1) remove edges , (2) remove small  objects
        mask_fill = mask_fill & ~mask_edge
        mask_fill = morphology.remove_small_objects(
            mask_fill.astype("bool"), obj_size_rem
        )

        # For edge - consider also freeline edge mask

        mask_edge = mask_edge.astype("bool")
        mask_edge = np.logical_or(mask_edge, mask_edge_freeline)

        # Assign to dictionary for return
        mask_dict["edge"] = mask_edge
        mask_dict["fill"] = mask_fill.astype("bool")
        mask_dict["labels"] = mask_labels.astype("uint16")

        if save_indiv is True:
            mask_dict["edge_indiv"] = mask_edge_indiv
            mask_dict["fill_indiv"] = mask_fill_indiv
        else:
            mask_dict["edge_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)
            mask_dict["fill_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)

    # Only edge mask present
    elif np.any(mask_edge_freeline):
        mask_dict["edge"] = mask_edge_freeline
        mask_dict["fill"] = mask_fill.astype("bool")
        mask_dict["labels"] = mask_labels.astype("uint16")

        mask_dict["edge_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)
        mask_dict["fill_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)

    else:
        raise Exception("No mask has been created.")

    return mask_dict


def generate_border_mask(labels, edge, border_detection_threshold=3):
    tmp = morphology.dilation(edge, morphology.square(7))
    # props = measure.regionprops(labels)
    msk0 = 255 * (labels > 0)
    msk0 = msk0.astype("uint8")

    msk1 = np.zeros_like(labels, dtype="bool")

    # max_area = np.max([p.area for p in props])

    for y0 in range(labels.shape[0]):
        for x0 in range(labels.shape[1]):
            if not tmp[y0, x0]:
                continue
            sz = border_detection_threshold

            uniq = np.unique(
                labels[
                    max(0, y0 - sz) : min(labels.shape[0], y0 + sz + 1),
                    max(0, x0 - sz) : min(labels.shape[1], x0 + sz + 1),
                ]
            )
            if len(uniq[uniq > 0]) > 1:
                msk1[y0, x0] = True
                msk0[y0, x0] = 0

    msk0 = 255 * (labels > 0)
    msk0 = msk0.astype("uint8")  # cell area
    msk1 = morphology.binary_closing(msk1)
    msk1 = 255 * msk1  # cell boundarys
    msk1 = msk1.astype("uint8")

    msk2 = np.zeros_like(labels, dtype="uint8")
    msk = np.stack((msk0, msk1, msk2))
    msk = np.rollaxis(msk, 0, 3)

    # Note: saved as float 16 - to plot has to be converted to float32
    # To be saved rescaled as 8 bit
    return msk.astype("float32")


def features_to_mask(features, image_size, mask_type="labels", **kwargs):
    if isinstance(features, dict) and "features" in features.keys():
        features = features["features"]

    if len(features) == 0:
        return np.zeros(image_size[:2], dtype="uint16")

    # Read annotation:  Correct class has been selected based on annot_type
    annot_dict_all, image_size = load_features(features, image_size)

    annot_types = set(
        annot_dict_all[k]["properties"]["label"] for k in annot_dict_all.keys()
    )
    mask_dict = None
    for annot_type in annot_types:
        # print("annot_type: ", annot_type)
        # Filter the annotations by label
        annot_dict = {
            k: annot_dict_all[k]
            for k in annot_dict_all.keys()
            if annot_dict_all[k]["properties"]["label"] == annot_type
        }
        # Create masks
        # Binary - is always necessary to creat other masks

        mask_dict = generate_binary_masks(
            annot_dict,
            image_size=image_size,
            erose_size=5,
            obj_size_rem=500,
            save_indiv=True,
        )
        if mask_type == "border":
            border_mask = generate_border_mask(
                mask_dict["labels"], mask_dict["edge"], **kwargs
            )
            mask_dict["border"] = border_mask

    if mask_type == "labels":
        return np.flipud(mask_dict["labels"])
    elif mask_type == "border":
        return np.flipud(mask_dict["border"])


def _convert_mask(img_mask, label=None, mask_type="labels"):
    # for img_mask, for cells on border, should make sure on border pixels are # set to 0
    img_mask = img_mask.copy()

    if mask_type == "border":
        # assumes two channel border mask
        # the first channel is the filled mask and the second channel is the borders
        mask = img_mask[:, :, 0] * (1 - (1 * img_mask[:, :, 1] > 0))
        mask = remove_small_objects(mask > 0, 8)
        markers = ndi.label(mask, output=np.uint32)[0]
        img_mask = watershed(mask, markers, mask=mask, watershed_line=True)

    shape_x, shape_y = img_mask.shape
    shape_x, shape_y = shape_x - 1, shape_y - 1
    img_mask[0, :] = img_mask[:, 0] = img_mask[shape_x, :] = img_mask[:, shape_y] = 0
    features = []
    label = label or "cell"
    # Get all object ids, remove 0 since this is background
    ind_objs = np.unique(img_mask)
    ind_objs = np.delete(ind_objs, np.where(ind_objs == 0))
    for obj_int in np.nditer(ind_objs, flags=["zerosize_ok"]):
        # Create binary mask for current object and find contour
        img_mask_loop = np.zeros((img_mask.shape[0], img_mask.shape[1]))
        img_mask_loop[img_mask == obj_int] = 1
        contours_find = measure.find_contours(img_mask_loop, 0.5)
        if len(contours_find) == 1:
            index = 0
        else:
            pixels = []
            for _, item in enumerate(contours_find):
                pixels.append(len(item))
            index = np.argmax(pixels)
        contour = contours_find[index]

        contour_as_numpy = contour[:, np.argsort([1, 0])]
        contour_as_numpy[:, 1] = np.array([img_mask.shape[0] - h[0] for h in contour])
        contour_asList = contour_as_numpy.tolist()

        # Create and append feature for geojson
        pol_loop = geojson_polygon([contour_asList])

        full_label = label + "_idx"
        index_number = int(obj_int - 1)
        features.append(
            Feature(
                geometry=pol_loop, properties={full_label: index_number, "label": label}
            )
        )
    return features


def mask_to_geojson(img_mask, label=None, mask_type="labels"):
    """
    Args:
      img_mask (numpy array): numpy data, with each object being assigned with a unique uint number
      label (str): like 'cell', 'nuclei'
    """
    features = _convert_mask(np.flipud(img_mask), label=label, mask_type=mask_type)
    feature_collection = FeatureCollection(
        features, bbox=[0, 0, img_mask.shape[1] - 1, img_mask.shape[0] - 1]
    )
    geojson_str = dumps(feature_collection, sort_keys=True)
    return geojson_str


def mask_to_features(img_mask, label=None, mask_type="labels"):
    """
    Args:
      img_mask (numpy array): numpy data, with each object being assigned with a unique uint number
      label (str): like 'cell', 'nuclei'
    """
    features = _convert_mask(np.flipud(img_mask), label=label, mask_type=mask_type)
    features = list(
        map(
            lambda feature: np.array(
                feature["geometry"]["coordinates"][0], dtype="uint16"
            ).tolist(),
            features,
        )
    )
    return features


async def fetch_image(url, name=None, grayscale=False, transpose=False, size=None):
    if is_pyodide:
        from js import fetch

        response = await fetch(url)
        bytes = await response.arrayBuffer()
        bytes = bytes.to_py()
        buffer = io.BytesIO(bytes)
    else:
        import requests

        response = requests.get(url)
        buffer = io.BytesIO(response.content)
    buffer.name = name or url.split("?")[0].split("/")[1]
    image = Image.open(buffer)
    if grayscale:
        image = image.convert("L")
    if size:
        image = image.resize(size=size)
    image = np.array(image).astype("float32")
    if transpose:
        image = image.transpose(2, 0, 1)
    return image
