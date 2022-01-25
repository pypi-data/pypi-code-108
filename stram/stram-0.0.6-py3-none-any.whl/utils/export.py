import cv2
import numpy as np


def create_styling_process_figure(
    content_image,
    style_image,
    synthesized_image,
    margin=12,
    background_colour=(0, 0, 0),
):
    """
    Create a figure that shows the styling process by concatenating the input images
    with the synthesized output result.

    Args:
        content_image (np.ndarray): the image on which the style was applied
        style_image (np.ndarray): the image whose style was applied
        synthesized_image (np.ndarray): the resulting image
        margin (int): number of pixels to leave in between images in the figure
        background_colour (tuple): RGB values to populate the background
    Returns:
        figure (np.ndarray): an image that presents the styling process
    """
    style_image_max_height = round(content_image.shape[0] * 1.25)
    style_image_max_width = round((content_image.shape[1] + margin) * 1.5)

    height_ratio = style_image_max_height / style_image.shape[0]
    width_ratio = style_image_max_width / style_image.shape[1]
    resizing_ratio = min(height_ratio, width_ratio)

    style_image_height = round(resizing_ratio * style_image.shape[0])
    style_image_width = round(resizing_ratio * style_image.shape[1])
    style_image_resized = cv2.resize(
        style_image,
        (style_image_width, style_image_height),
        interpolation=cv2.INTER_LINEAR,
    )

    figure_height = content_image.shape[0] + style_image_height + 3 * margin
    figure_width = content_image.shape[1] + synthesized_image.shape[1] + 3 * margin
    figure = np.uint8(background_colour) * np.ones(
        (figure_height, figure_width, 3), dtype=np.uint8
    )

    horiz_offset = (figure_width - style_image_width) // 2
    figure[
        margin : margin + style_image_height,
        horiz_offset : horiz_offset + style_image_width,
    ] = style_image_resized

    vert_offset = 2 * margin + style_image_height
    figure[vert_offset:-margin, margin : margin + content_image.shape[1]] = content_image
    figure[
        vert_offset:-margin, -(margin + synthesized_image.shape[1]) : -margin
    ] = synthesized_image

    return figure
