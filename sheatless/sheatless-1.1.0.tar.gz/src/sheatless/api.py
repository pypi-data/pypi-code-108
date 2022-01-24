from io import BytesIO
import cv2
import pdf2image
import numpy as np

from .engine import get_instruments_dict, predict_parts_in_imgs, generateImagesFromPdf

from .engine import predict_parts_in_img
"""
def predict_parts_in_img(img : io.BytesIO | bytes | PIL.Image.Image, instruments, use_lstm=False, tessdata_dir=None) -> typing.Tuple[list, list]:
    Arguments:
    - img                     - image object
    - instruments             - dictionary of instruments
    - use_lstm     (optional) - Use LSTM instead of legacy engine mode.
    - tessdata_dir (optional) - Full path to tessdata directory. If not provided, whatever the environment variable TESSDATA_DIR will be used.

    Returns:
    - partNames               - a list of part names
    - instrumentses           - a list of lists of instruments for each part
"""

def predict_parts_in_pdf(
	pdf : BytesIO | bytes,
	instruments=None,
	instruments_file=None,
	instruments_file_format="yaml",
	use_lstm=False,
	tessdata_dir=None,
	):
	"""
	Arguments:
	- pdf                                - PDF file object
	- instruments             (optional) - Dictionary of instruments. Will override any provided instruments file.
	- instruments_file        (optional) - Full path to instruments file or instruments file object. Accepted extensions: .yaml, .yml, .json
	- instruments_file_format (optional) - Format of instruments_file if it is a file object. Accepted formats: yaml, json
	  - If neither instruments_file nor instruments is provided a default instruments file will be used.
	- use_lstm                (optional) - Use LSTM instead of legacy engine mode.
	- tessdata_dir            (optional) - Full path to tessdata directory. If not provided, whatever the environment variable TESSDATA_DIR will be used.

	Returns:
	- parts                              - A list of dictionaries { "name": "name", "instruments": ["instrument 1", "instrument 2"...] "fromPage": i, "toPage": j } describing each part
	- instrumentsDefaultParts            - A dictionary { ..., "instrument_i": j, ... }, where j is the index in the parts list for the default part for instrument_i.
	"""
	instruments = get_instruments_dict(
		instruments=instruments,
		instruments_file=instruments_file,
		instruments_file_format=instruments_file_format,
	)
	if type(pdf) == BytesIO:
		pdf = pdf.getvalue()
	imgs = pdf2image.convert_from_bytes(pdf, dpi=200)
	imgs = [np.array(img) for img in imgs]
	return predict_parts_in_imgs(imgs, instruments, use_lstm=use_lstm, tessdata_dir=tessdata_dir)


def processUploadedPdf(pdfPath, imagesDirPath, instruments_file=None, instruments=None, use_lstm=False, tessdata_dir=None):
	"""
	Arguments:
	- pdfPath                     - Full path to PDF file
	- imagesDirPath               - Full path to output images
	- instruments_file (optional) - Full path to instruments file. Accepted formats: YAML (.yaml, .yml), JSON (.json)
	- instruments      (optional) - Dictionary of instruments. Will override any provided instruments file.
	  - If neither instruments_file nor instruments is provided a default instruments file will be used.
	- use_lstm         (optional) - Use LSTM instead of legacy engine mode.
	- tessdata_dir     (optional) - Full path to tessdata directory. If not provided, whatever the environment variable TESSDATA_DIR will be used.

	Returns:
	- parts                       - A list of dictionaries { "name": "name", "instruments": ["instrument 1", "instrument 2"...] "fromPage": i, "toPage": j } describing each part
	- instrumentsDefaultParts     - A dictionary { ..., "instrument_i": j, ... }, where j is the index in the parts list for the default part for instrument_i.
	"""
	instruments = get_instruments_dict(
		instruments=instruments,
		instruments_file=instruments_file,
	)
	
	imagePaths = generateImagesFromPdf(pdfPath, imagesDirPath, 1, None)
	imgs = [cv2.imread(imagePath) for imagePath in imagePaths]

	return predict_parts_in_imgs(imgs, instruments, use_lstm=use_lstm, tessdata_dir=tessdata_dir)

