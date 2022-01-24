import os
import io
from io import BytesIO
from types import NoneType
import typing
from typing import Type
import numpy as np
import cv2
import pdf2image
import time
import pytesseract
import yaml
import json
import difflib
import unidecode
import PIL

# print("Hello sheet music")

def generateImagesFromPdf(pdfPath, outputDir, startPage, endPage):
	print("Generating images from ", pdfPath, "...", sep="")
	print()
	images = pdf2image.convert_from_path(pdfPath, dpi=200, first_page=startPage, last_page=endPage)
	generatedImages = []
	for i in range(len(images)):
		path = f"{outputDir}/page_{i+1}.jpg"
		print("Generated image from pdf:", path)
		images[i].save(path)
		generatedImages.append(path)
	print()
	return generatedImages

def textRecognizer(imagePath):
	img = cv2.imread(imagePath)
	imgWithBoxes = img.copy()
	res = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
	filtered = {}
	for key in res:
		filtered[key] = []
	for i in range(len(res["text"])):
		if int(res["conf"][i]) > 10 and res["text"][i].strip(" ") != "":
			for key in res:
				filtered[key].append(res[key][i])
			x1 = res["left"][i]
			y1 = res["top"][i]
			x2 = x1 + res["width"][i]
			y2 = y1 + res["height"][i]
			print(x1, y1, x2, y2)
			cv2.rectangle(imgWithBoxes, (x1, y1), (x2, y2), (0, 0, 255), thickness=2) # (, res["top"]), (res["left"] + , res["top"] + res["width"]), (0, 0, 255))
	for key in filtered:
		print("{:>10}".format(key), end=": ")
		for i in range(len(filtered[key])):
			print("{:>10}".format(filtered[key][i]), end=" ")
		print()
	print(pytesseract.image_to_string(img))
	cv2.imshow("Text recognition", imgWithBoxes)
	cv2.waitKey(0)

def cropImage(img):
	return img
	return img[0:len(img)//2, 0:len(img[0])//2]

def processDetectionData(detectionData, img):
	imgWithBoxes = img.copy()
	nicePrint  = "+------------------------------+------------+----------+----------+\n"
	nicePrint += "| text                         | confidence | pos_left | pos_top  |\n"
	nicePrint += "+------------------------------+------------+----------+----------+\n"
	for i in range(len(detectionData["text"])):
		if int(detectionData["level"][i]) == 5:
			x1 = detectionData["left"][i]
			y1 = detectionData["top"][i]
			x2 = x1 + detectionData["width"][i]
			y2 = y1 + detectionData["height"][i]
			cv2.rectangle(imgWithBoxes, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
			nicePrint += "| {:28} | {:>10} | {:>8} | {:>8} |\n".format(detectionData["text"][i],
				detectionData["conf"][i], detectionData["left"][i], detectionData["top"][i])
	nicePrint += "+------------------------------+------------+----------+----------+\n"
	return imgWithBoxes, nicePrint

class Detection:
	# This class describes a single text detection from tesseract
	# Meaning of variables is same as the raw tesseract output, an explanation can be found here:
	# https://www.tomrochette.com/tesseract-tsv-format

	__level = 1
	__page_num = 1
	__block_num = 0
	__par_num = 0
	__line_num = 0
	__word_num = 0
	__left = 0
	__top = 0
	__width = 0
	__height = 0
	__conf = 0
	__text = ""

	def __init__(self, detectionData, i):
		self.__level = detectionData["level"][i]
		self.__page_num = detectionData["page_num"][i]
		self.__block_num = detectionData["block_num"][i]
		self.__par_num = detectionData["par_num"][i]
		self.__line_num = detectionData["line_num"][i]
		self.__word_num = detectionData["word_num"][i]
		self.__left = detectionData["left"][i]
		self.__top = detectionData["top"][i]
		self.__width = detectionData["width"][i]
		self.__height = detectionData["height"][i]
		self.__conf = detectionData["conf"][i]
		self.__text = detectionData["text"][i]
	
	# Straightforward get functions
	def level(self): return self.__level
	def page_num(self): return self.__page_num
	def block_num(self): return self.__block_num
	def par_num(self): return self.__par_num
	def line_num(self): return self.__line_num
	def word_num(self): return self.__word_num
	def left(self): return self.__left
	def top(self): return self.__top
	def width(self): return self.__width
	def height(self): return self.__height
	def conf(self): return self.__conf
	def text(self): return self.__text

	# Useful other get functions:
	def right(self): return self.__left + self.__width
	def bot(self): return self.__top + self.__height



def isSimilarEnough(detectedText, keyword):
	return difflib.SequenceMatcher(None, unidecode.unidecode_expect_ascii(detectedText.lower()),
		unidecode.unidecode_expect_ascii(keyword.lower())).ratio() > 0.9
		# or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"s", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"es", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"r", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"er", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"as", keyword.lower()).ratio() > 0.9
	return detectedText.lower() == keyword.lower()

def predictParts(detectionData, instruments, imageWidth, imageHeight):
	# return partNames, instrumentses
	# Here, input instruments should be a dict where the keyes are instrument names and values are lists of keywords
	# The instrument names could also be the instruments id in the database, it is only used as an identifier

	# Firstly, convert detectionData to handy Detection objects
	detections = []
	for i in range(len(detectionData["text"])):
		detections.append(Detection(detectionData, i))

	# Secondly, gather a list of all matches between detected texts and instruments
	matches = []
	exceptionMatches = []
	for instrument in instruments:
		for j in range(len(instruments[instrument]["include"])):
			keyword = instruments[instrument]["include"][j]
			N = len(keyword.split(" "))
			for i in range(len(detections)-(N-1)):
				if detections[i].level() != 5: continue;
				blockNr = detections[i].block_num()
				sameBlock = True
				for k in range(1, N):
					if detections[i+k].block_num() != blockNr:
						sameBlock = False;
						break;
				if sameBlock:
					detectedWords = detections[i:i+N]
					for l in range(len(detectedWords)):
						detectedWords[l] = detectedWords[l].text()
					detectedText = " ".join(detectedWords)
					if isSimilarEnough(detectedText, keyword):
						matches.append({"i": i, "instrument": instrument, "keyword": keyword})

		for j in range(len(instruments[instrument]["exceptions"])):
			keyword = instruments[instrument]["exceptions"][j]
			N = len(keyword.split(" "))
			for i in range(len(detections)-(N-1)):
				if detections[i].level() != 5: continue;
				blockNr = detections[i].block_num()
				sameBlock = True
				for k in range(1, N):
					if detections[i+k].block_num() != blockNr:
						sameBlock = False;
						break;
				if sameBlock:
					detectedWords = detections[i:i+N]
					for k in range(len(detectedWords)):
						detectedWords[k] = detectedWords[k].text()
					detectedText = " ".join(detectedWords)
					if isSimilarEnough(detectedText, keyword):
						exceptionMatches.append({"i": i, "instrument": instrument, "keyword": keyword})

	# Lastly, predict how many, what names, and for what instruments the parts are
	if len(matches) == 0:
		return [], []
	else:
		blocksWithMatches = set()
		for match in matches:
			excepted = False
			for exception in exceptionMatches:
				if match["instrument"] == exception["instrument"] and \
					detections[match["i"]].block_num() == detections[exception["i"]].block_num():
					excepted = True; break
			if not excepted:
				blocksWithMatches.add(detections[match["i"]].block_num())
			
		nrOfBlocksWithMatches = len(blocksWithMatches)
		if nrOfBlocksWithMatches <= 2:
			partNames = []
			instrumentses = []
			for blockNr in blocksWithMatches:
				partName = []
				instrumentsWithMatchesInBlock = set()
				for i in range(len(detections)):
					if detections[i].level() == 5 and detections[i].block_num() == blockNr:
						partName.append(detections[i].text())
						for match in matches:
							if match["i"] == i:
								excepted = False
								for exception in exceptionMatches:
									if exception["instrument"] == match["instrument"] and \
										detections[exception["i"]].block_num() == blockNr:
										excepted = True; break
								if not excepted:
									instrumentsWithMatchesInBlock.add(match["instrument"])
				partName = " ".join(partName)
				partNames.append(partName)
				instrumentses.append(list(instrumentsWithMatchesInBlock))
			return partNames, instrumentses
		else:
			# Its probably a full score
			return ["full score"], [["full score"]]


def predict_parts_in_img(img : io.BytesIO | bytes | PIL.Image.Image, instruments, use_lstm=False, tessdata_dir=None) -> typing.Tuple[list, list]:
	if type(img) is PIL.Image.Image:
		pass
	elif type(img) is io.BytesIO:
		img = PIL.Image.open(img)
	elif type(img) is bytes:
		img = PIL.Image.open(io.BytesIO(img))

	config = "--user-words sheetmusicUploader/instrumentsToLookFor.txt --psm 11 --dpi 96 -l eng"
	if use_lstm: config += " --oem 1"
	if tessdata_dir != None: config += " --tessdata-dir \""+tessdata_dir+"\""
	detection_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)

	return predictParts(detection_data, instruments, *img.size)


def predict_parts_in_imgs(imgs, instruments, use_lstm=False, tessdata_dir=None):
	"""
	Arguments:
	- imgs                    - a list of images representing one page each in a pdf
	- instruments             - a dictionary of instruments
	- use_lstm=False          - to use LSTM engine mode instead of legacy
	- tessdata_dir=None       - full path to tessdata_dir

	Returns:
	- parts                   - a list of dictionaries { "name": "[name]", "fromPage": i, "toPage": j } describing each part
	- instrumentsDefaultParts - a dictionary { ..., "instrument_i": j, ... }, where j is the index in the parts list for the default part for instrument_i.
	"""
	parts = []
	instrumentsDefaultParts = { instrument: None for instrument in instruments }
	instrumentsDefaultParts["full score"] = None
	lastPartName = ""
	lastPartNamePage = 0
	lastInstruments = []
	for i in range(len(imgs)):
		print("side", i+1, "av", len(imgs))
		print("cropper...")
		img = cropImage(imgs[i])
		print("detecter...")
		config = "--user-words sheetmusicUploader/instrumentsToLookFor.txt --psm 11 --dpi 96 -l eng"
		if use_lstm: config += " --oem 1"
		if tessdata_dir != None: config += " --tessdata-dir \""+tessdata_dir+"\""
		detectionData = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
		print("predicter...")
		partNames, instrumentses = predictParts(detectionData, instruments, img.shape[1], img.shape[0])
		print("partNames:", partNames, "instrumentses:", instrumentses)
		for j in range(len(partNames)):
			print(j, lastPartName)
			if lastPartName:
				parts.append({
					"name": lastPartName,
					"instruments": lastInstruments,
					"fromPage": lastPartNamePage,
					"toPage": i if j == 0 else i+1
				})
				for k in range(len(lastInstruments)):
					if instrumentsDefaultParts[lastInstruments[k]] == None:
						instrumentsDefaultParts[lastInstruments[k]] = len(parts)-1
			lastPartName = partNames[j]
			lastPartNamePage = i+1
			lastInstruments = instrumentses[j]
	if lastPartName:
		parts.append({
			"name": lastPartName,
			"instruments": lastInstruments,
			"fromPage": lastPartNamePage,
			"toPage": len(imgs)
		})
		for k in range(len(lastInstruments)):
			if instrumentsDefaultParts[lastInstruments[k]] == None:
				instrumentsDefaultParts[lastInstruments[k]] = len(parts)-1
	return parts, instrumentsDefaultParts


def get_instruments_dict_from_file_stream(file, format="yaml"):
	match format:
		case "yaml":
			return yaml.safe_load(file)
		case "json":
			return json.load(file)
		case _:
			raise Exception(f"Instruments file format {format} is not supported. Supported formats are yaml, json")


def get_instruments_dict_from_file_path(instruments_file_path):
	with open(instruments_file_path) as file:
		_, file_extension = os.path.splitext(instruments_file_path)
		if file_extension.lower() in [".yaml", ".yml"]:
			return get_instruments_dict_from_file_stream(file)
		elif file_extension.lower() in [".json"]:
			return get_instruments_dict_from_file_stream(file, "json")
		else:
			raise Exception(f"Instruments file with extension {file_extension} is not supported. Supported extensions are .yaml, .yml, .json")

def get_instruments_dict(
	instruments_file : Type[None] | str | BytesIO | bytes = None,
	instruments_file_format="yaml",
	instruments=None
	):
	if instruments is not None:
		return instruments
	match instruments_file:
		case NoneType():
			return get_instruments_dict_from_file_path(os.path.join(os.path.dirname(__file__), "instruments.yaml"))
		case str():
			return get_instruments_dict_from_file_path(instruments_file)
		case BytesIO():
			return get_instruments_dict_from_file_stream(instruments_file, format=instruments_file_format)
		case bytes():
			return get_instruments_dict_from_file_stream(BytesIO(instruments_file), format=instruments_file_format)
