import os
import tempfile

import fitz
from rich import print
import imageio

from pdf_crop import helper


class PymuPDFCrop(object):
    def __init__(self, input_file, dpi=128, threshold=0.008, space=2):
        self._input_file = input_file
        self._input_pdf = fitz.open(input_file)
        self._page_count = self._input_pdf.page_count
        self._dpi = dpi
        self._space = space
        self._threshold = threshold

    def crop(self, page_no, output_file=None, crop_box=None):
        if page_no >= self._page_count:
            print("[red]page no exceed the page number[/red]")
            return
        page = self._input_pdf[page_no]
        if crop_box is None:
            crop_box = self.detect_margin(page)
        page.set_cropbox(crop_box)

        return self.save_pdf(page, output_file), page.mediabox, crop_box

    def page_count(self):
        return self._page_count

    def detect_margin(self, page):
        # Save temporary png file
        tmp_png = tempfile.gettempdir() + os.path.sep + "detect_crop_box.png"
        pix = page.get_pixmap(dpi=self._dpi)
        pix.save(tmp_png)
        origin_rect = page.mediabox
        media_width = origin_rect[2] - origin_rect[0]
        media_height = origin_rect[3] - origin_rect[1]

        image = imageio.imread(tmp_png)
        detect_rect = helper.detect_frame(image, self._space, self._threshold)

        result_rect = [
            int(detect_rect[0] * media_width),
            int(detect_rect[1] * media_height),
            int(detect_rect[2] * media_width),
            int(detect_rect[3] * media_height),
        ]
        return fitz.Rect(result_rect)

    def save_pdf(self, page, output_file):
        page_no = page.number
        output_pdf = fitz.open()
        output_pdf.insert_pdf(self._input_pdf, from_page=page_no, to_page=page_no)
        if output_file is None or len(output_file) == 0:
            input_prefix = os.path.splitext(self._input_file)[0]
            output_file = f"{input_prefix} - page {page_no:2d}.pdf"
        output_pdf.save(output_file)
        return output_file
