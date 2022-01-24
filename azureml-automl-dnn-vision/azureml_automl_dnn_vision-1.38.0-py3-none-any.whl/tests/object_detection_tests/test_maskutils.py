import itertools
import numpy
import torch
from PIL import Image

from azureml.automl.dnn.vision.object_detection.common import masktools

# Maximum Porportion of Mask Pixels That Can Change During Mask -> Polygon -> Mask Conversion
TOLERANCE = 0.05
TEST_IMAGE_FILE = 'object_detection_data/images/000001818.png'
TEST_BOUNDARY = [[220, 90, 225, 190, 315, 170, 310, 80]]  # Rough mask boundary in image


def convert_polygon_to_mask(contours, h, w):
    # Combines Two Key MaskTools Functions to convert polygon contours to a binay mask
    rle_mask = masktools.convert_polygon_to_rle_masks(contours, h, w)
    return masktools.decode_rle_masks_as_binary_mask(rle_mask)


def build_square_primitve(i, j, h=100, w=150, h_splits=3, w_splits=3):
    # Builds a mask where a rectangle of pixels are filled in.
    # h_splits is how many evenly sized columns the pixel mask is split into
    # w_splits is now many evanly spaced rowd the pixel mask is split into
    # i is the row index for the rectangle of pixels to be filled in
    # j is the column index for the rectangle of pixels to be filled in

    h_inc, w_inc = (1. * h) / h_splits, (1. * w) / w_splits

    new_primitive = numpy.zeros((h, w), numpy.uint8)
    new_primitive[int(i * h_inc):int((i + 1) * h_inc),
                  int(j * w_inc):int((j + 1) * w_inc)] = 1

    return new_primitive


def build_diagonal_primitive(l_stripe=True, r_stripe=True, h=100, w=150, l_width=20, r_width=20):
    # Build a mask where a diagonal stripe of pixels are filled in
    # l_stripe: Turns on a stripe that starts at the upper left corner
    # r_stripe: Turns on a stripe that starts at the lower left corner
    # l_width: width of the upper left corner stripe
    # r_width: width of the lower left corner stripe

    l_stripe_primitive = numpy.zeros((h, w), numpy.uint8)
    r_stripe_primitive = numpy.zeros((h, w), numpy.uint8)

    for i in range(h):
        for j in range(w):
            if l_stripe:
                if (i + l_width) > (j / (1. * w)) * h:
                    l_stripe_primitive[i, j] = 1
                if (i - l_width) > (j / (1. * w)) * h:
                    l_stripe_primitive[i, j] = 0

            if r_stripe:
                if (h - (i - r_width)) > (j / (1. * w)) * h:
                    r_stripe_primitive[i, j] = 1
                if (h - (i + r_width)) > (j / (1. * w)) * h:
                    r_stripe_primitive[i, j] = 0

    new_primitive = l_stripe_primitive | r_stripe_primitive

    return new_primitive


def invert_primitive(synthetic_mask):
    # Takes a mask and reverse the pixel values

    return ~synthetic_mask - 254


def denormalize_contours(contours, h, w):
    # Takes the normalized contours and converts them to image coordinates
    denormalized_contours = []

    for contour in contours:
        denormalized_contour = [0] * len(contour)
        denormalized_contour[::2] = [w * x for x in contour[::2]]
        denormalized_contour[1::2] = [h * y for y in contour[1::2]]
        denormalized_contours.append(denormalized_contour)

    return denormalized_contours


def check_mask_conversion(mask):
    # Converts a mask to a polyogn, then converts the polygon back to a mask
    # Checks to see how close the recovered mask is to the original mask
    # Returns # of different pixels / # of pixels in the original mask

    h, w = mask.shape

    mask_tensor = torch.tensor(mask)
    mask_tensor = mask_tensor.unsqueeze(0)

    rle_mask = masktools.encode_mask_as_rle(mask_tensor)
    contours = masktools.convert_mask_to_polygon(rle_mask)
    denormalized_contour = denormalize_contours(contours, h, w)
    recovered_mask = convert_polygon_to_mask(denormalized_contour, h, w)

    missed_pixel_ratio = numpy.sum(numpy.abs(recovered_mask - mask) > 0) / numpy.sum(mask)

    return missed_pixel_ratio


def mask_combine(mask_list, index_list, h=100, w=150):
    # Takes a list of masks, and list of indices of theses masks
    # And combine the masks at those indices in the list into one mask

    base_mask = numpy.zeros((h, w), numpy.uint8)

    combo_masks = [mask_list[i] for i in index_list]

    for mask in combo_masks:
        base_mask |= mask

    return base_mask


class TestMaskTools:

    def test_polygon_conversion(self):
        # Create a large number of synthetic masks, and check
        # how well the mask -> polygon -> mask preserves the mask
        # Will fail if any conversion has pixel errors that exceed threshold

        mask_primitives = []

        for i in range(3):
            for j in range(3):
                mask_primitives.append(build_square_primitve(i, j))

        mask_primitives.append(build_diagonal_primitive(l_stripe=True, r_stripe=False))
        mask_primitives.append(build_diagonal_primitive(l_stripe=False, r_stripe=True))
        mask_primitives.append(invert_primitive(build_diagonal_primitive(l_stripe=True, r_stripe=False)))
        mask_primitives.append(invert_primitive(build_diagonal_primitive(l_stripe=False, r_stripe=True)))

        number_of_primitives = len(mask_primitives)
        mask_indices = list(range(number_of_primitives))

        for i in range(1, number_of_primitives):
            for combo_indices in itertools.combinations(mask_indices, i):
                combo_primitive = mask_combine(mask_primitives, combo_indices)
                assert check_mask_conversion(combo_primitive) < TOLERANCE

    def test_grabcut_refine(self):
        # Runs a grabcut refine on a test image with a rough mask
        # Will fail if the function fails to return an appropriate size mask

        test_image = Image.open(TEST_IMAGE_FILE)
        w, h = test_image.size
        test_rough_image_mask = convert_polygon_to_mask(TEST_BOUNDARY, h, w)

        test_refined_mask = masktools.grabcut_mask_refine(
            test_image, test_rough_image_mask)

        refined_h, refined_w = test_refined_mask.shape
        original_h, original_w = test_rough_image_mask.shape

        assert refined_h == original_h
        assert refined_w == original_w
