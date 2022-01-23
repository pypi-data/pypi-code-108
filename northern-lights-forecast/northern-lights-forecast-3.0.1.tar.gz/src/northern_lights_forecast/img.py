"""Sort out colours from an image.

This script finds all pixels with colour within a range a colours, while all
other is coloured black. From
https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
"""
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pytesseract

__PLACE__ = {
    "Ny-Ålesund": "nal1a",
    "Tromsø": "tro2a",
    "Longyearbyen": "lyr2a",
    "Hopen": "hop1a",
    "Bjørnøya": "bjn1a",
    "Jan Mayen": "jan1a",
    "Nordkapp": "nor1a",
    "Andenes": "and1a",
    "Røst": "rst1a",
    "Jackvik": "jck1a",
    "Dønna": "don1a",
    "Rørvik": "rvk1a",
    "Dombås": "dob1a",
    "Solund": "sol1a",
    "Harestua": "har1a",
    "Karmøy": "kar1a",
    "Brorfelde": "bfe6d",
    "Rømø": "reo1d",
    "Hov": "hov1d",
    "Savissivik": "svs1d",
    "Kullorsuaq": "kuv1d",
    "Upernavik": "upn1d",
    "Summit": "sum1d",
    "Uummannaq": "umq1d",
    "Attu": "atu1d",
    "Kangerlussuaq/Sendre Stromfjord": "stf1d",
    "Nuuk/Godthåp": "ghb1d",
    "Paamiut/Frederikshåp": "fhb1d",
    "Narsarsuaq": "naq4d",
    "Danmarkshavn": "dmh1d",
    "Ammassalik": "amk1f",
}


def download(location: str) -> np.ndarray:
    """Download a `.gif` file, return as `.jpg`.

    Parameters
    ----------
    location: str
        Geographical location of magnetometer generating the file to download

    Returns
    -------
    np.ndarray:
        the downloaded file as `.jpg`
    """
    loc = __PLACE__[location]
    url = f"https://flux.phys.uit.no/Last24/Last24_{loc}.gif"
    return plt.imread(url, format="jpg")[:, :, :3]


def read(image: np.ndarray) -> float:
    """Read the scaling of the axis of the downloaded file. See `download()`.

    Parameters
    ----------
    image: np.ndarray
        The input file

    Returns
    -------
    float
        scaling factor of y axis to pixels
    """
    # Cut out the scale on the y-axis
    images = np.hstack([image[360:530, 1:55, :]])
    # Pick the grey scale
    images = images[:, :, 0]
    # Make it clearer, b/w, with threshold
    threshold = 150
    images[images < threshold] = 0
    images[images >= threshold] = 255
    # Read digits in image with tesseract
    data = pytesseract.image_to_boxes(
        images,
        lang="eng",
        config="--psm 6 digits --oem 3 -c tessedit_char_whitelist=0123456789",
    )

    # Extract scales from strings
    d = data.split("\n")
    d = [data for data in d if len(data) > 1]
    d = d[::-1]  # Reverse
    c = 0
    y_level = 0
    lim_0 = ""
    y_0 = ""
    lim_1 = ""
    y_1 = ""
    for ell in d:
        ell = ell.split()
        # if ell[0] != "-" and y_level != int(ell[2]):
        if y_level != int(ell[2]):
            y_level = int(ell[2])
            c += 1
        if c == 1:
            lim_0 += ell[0]
            y_0 = ell[2]
        elif c == 2:
            lim_1 += ell[0]
            y_1 = ell[2]
        if c >= 3:
            break
    lim_b = float(lim_0[::-1])
    y_b = float(y_0)
    lim_t = float(lim_1[::-1])
    y_t = float(y_1)
    # Calculate the scale along the y-axis using the values and their position in the
    # image
    return 1 / round(abs(lim_t - lim_b) / abs(y_t - y_b), 4)


def find_colour(image: np.ndarray) -> np.ndarray:
    """Isolate the blue pixels in a RGB image.

    Parameters
    ----------
    image: np.ndarray
        The input file

    Returns
    -------
    np.ndarray
        New image with red and green channels set to zero
    """
    image[:, :, 0] = 0
    image[:, :, 1] = 0

    # # === < Show figures > ===
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.imshow(image)
    # # plt.savefig('before.png', dpi=200)
    # # plt.figure()
    # # plt.imshow(output)
    # # plt.show()
    # # === </ Show figures > ===
    # Save the black/white image of the blue structures
    return image


def img_analysis(location: str) -> Tuple[float, np.ndarray]:
    """Analyse image for a colour and return the scaling of the plot axis in the image.

    Parameters
    ----------
    location: str
        Geographical location of magnetometer creating the image.

    Returns
    -------
    float:
        The scaling to make pixels and value axis in plot equal.
    np.ndarray
        Cropped image, the interesting part to do a line fit to.
    """
    # Download image
    image = download(location)
    scaling = read(image)
    # Crop image
    y_h = int(image.shape[0] * 0.4)
    x_h = int(image.shape[1] * 0.1)
    image = np.hstack([image[y_h:, x_h:, :]])

    # Find colour of a given image and set to white,
    # the rest is set to black. Then save.
    im = find_colour(image)

    return scaling, im


def main() -> None:
    """Run 'img.py'."""
    img_analysis("Tromsø")


if __name__ == "__main__":
    main()
