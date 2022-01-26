from io import BytesIO
import sys
import pdf2image
import pytesseract
import numpy as np
from .engine import get_instruments_dict, cropImage, predictParts
from PyPDF2 import PdfFileReader

class PdfPredictor():
    def __init__(
        self,
        pdf : BytesIO | bytes,
        instruments=None,
        instruments_file=None,
        instruments_file_format="yaml",
        use_lstm=False,
        tessdata_dir=None,
        log_stream=sys.stdout
        ):
        self.instruments = get_instruments_dict(
            instruments=instruments,
            instruments_file=instruments_file,
            instruments_file_format=instruments_file_format,
        )
        self.pdf = pdf
        if type(self.pdf) == BytesIO:
            self.pdf = self.pdf.getvalue()
        self.use_lstm = use_lstm
        self.tessdata_dir = tessdata_dir
        self.log_stream = log_stream
    
    def log(self, *msg):
        print(*msg, file=self.log_stream)

    def parts(self):
        lastPartName = ""
        lastPartNamePage = 0
        lastInstruments = []
        pdfReader = PdfFileReader(BytesIO(self.pdf))
        for i in range(pdfReader.getNumPages()):
            self.log("page", i+1, "of", pdfReader.getNumPages())
            img = pdf2image.convert_from_bytes(self.pdf, dpi=200, first_page=i+1, last_page=i+1)[0]
            img = np.array(img)
            self.log("cropping...")
            img = cropImage(img)
            self.log("detecting...")
            config = "--user-words sheetmusicUploader/instrumentsToLookFor.txt --psm 11 --dpi 96 -l eng"
            if self.use_lstm: config += " --oem 1"
            if self.tessdata_dir != None: config += " --tessdata-dir \""+self.tessdata_dir+"\""
            detectionData = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
            self.log("predicting...")
            partNames, instrumentses = predictParts(detectionData, self.instruments, img.shape[1], img.shape[0])
            self.log("partNames:", partNames, "instrumentses:", instrumentses)
            for j in range(len(partNames)):
                self.log(j, lastPartName)
                if lastPartName == partNames[j]:
                    continue
                if lastPartName:
                    yield {
                        "name": lastPartName,
                        "instruments": lastInstruments,
                        "fromPage": lastPartNamePage,
                        "toPage": i if j == 0 else i+1
                    }
                lastPartName = partNames[j]
                lastPartNamePage = i+1
                lastInstruments = instrumentses[j]
        if lastPartName:
            yield {
                "name": lastPartName,
                "instruments": lastInstruments,
                "fromPage": lastPartNamePage,
                "toPage": pdfReader.getNumPages()
            }

