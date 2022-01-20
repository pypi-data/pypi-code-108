# encoding: utf-8
"""
@author: zyl
@file: pdf_processing.py
@time: 2022/1/20 10:32
@desc:
"""
from pdf2image import convert_from_path

from zyl_utils.data_utils.image_processing import ImageProcessor

IMAGEPROCESSOR = ImageProcessor()

import fitz
import pdfplumber
from tabula import read_pdf


class PDFProcessor:
    def __init__(self):
        pass

    @staticmethod
    def extract_tables_from_non_scanned_pdf(pdf: str, start_page: int = 0, end_page: int = None,
                                            method='tabula'):
        """extract tables from a pdf

        Args:
            pdf: PDF File
            start_page: the first page to begin extract,from 0 to start
            end_page: the last page to extract
            method:

        Returns:
            table_list : list/dict
        """
        pdf_object = pdfplumber.open(pdf)
        pdf_pages = pdf_object.pages[start_page:] if end_page is None else pdf_object.pages[
                                                                           start_page:end_page + 1]
        tables = []
        for i in range(len(pdf_pages)):
            if method == 'tabula':
                tables_df = read_pdf(pdf, pages=start_page + i + 1, multiple_tables=True)
                for t in tables_df:
                    table = []
                    table.append(list(t.columns))
                    for j in range(len(t)):
                        table.append(list(t.iloc[j]))
                    tables.append(table)
            else:  # 'pdfplumber'
                table = pdf_pages[i].extract_tables()
                for t in table:
                    if t:
                        tables.append(t)
        return tables

    @staticmethod
    def get_text_from_pdf_area(pdf_page, left, top, right, bottom, mode='text'):
        # clip = fitz.Rect(0, start_height, pdf_page.rect.width, tables[i]['top'])
        clip = fitz.Rect(left, top, right, bottom)
        if mode == 'text':
            ss = '\n'
        else:
            ss = ' '

        text = ''
        lines_texts = pdf_page.get_textpage(clip=clip).extractBLOCKS()
        last_line_bottom = 0
        for l in range(len(lines_texts)):
            if (last_line_bottom - lines_texts[l][1]) < 0.1 * (lines_texts[l][3] - lines_texts[l][1]):
                text += '\n'
                last_line_bottom = max(last_line_bottom, lines_texts[l][3])

            spans = lines_texts[l][4].split('\n')
            for s in range(len(spans) - 1):
                if spans[s] in spans[s + 1]:
                    continue
                else:
                    text += (str(spans[s]) + ss)
        return text

    @staticmethod
    def get_texts_and_tables_from_pdf(pdf, ocr_method='pharmcube_ocr'):
        images = convert_from_path(pdf, dpi=72)
        pdf_doc = fitz.Document(pdf)
        pdf_texts = ''
        all_tables = []
        for pg in range(0, len(images)):
            img = images[pg]
            pdf_page = pdf_doc.load_page(pg)
            if not pdf_page.get_text():
                is_scanned = True
                img = img.crop((10, 10, pdf_page.rect.width - 10, pdf_page.rect.height - 10))
            else:
                is_scanned = False
            tables, tables_location = IMAGEPROCESSOR.get_tables_from_image(img, ocr_method)
            all_tables.extend(tables)
            text_page = ''
            if tables_location:
                start_height = 0
                for i in range(len(tables_location)):
                    if tables_location[i][1] < start_height:
                        continue
                    if is_scanned:
                        text_area = IMAGEPROCESSOR.get_text_from_one_image(img, method=ocr_method)
                        text_page += text_area
                    else:
                        text_area = PDFProcessor.get_text_from_pdf_area(pdf_page, left=0, top=start_height,
                                                                        right=pdf_page.rect.width,
                                                                        bottom=tables_location[i][1])
                        text_page += (text_area + '\n<表格>\n')

                        start_height = tables_location[i][-1]
                        if i == (len(tables_location) - 1):
                            text_area = PDFProcessor.get_text_from_pdf_area(pdf_page, left=0, top=start_height,
                                                                            right=pdf_page.rect.width,
                                                                            bottom=pdf_page.rect.height)
                            text_page += text_area
            else:
                if is_scanned:
                    text_page = IMAGEPROCESSOR.get_text_from_one_image(img, method=ocr_method)
                else:
                    text_page = PDFProcessor.get_text_from_pdf_area(pdf_page, left=0, top=0,
                                                                     right=pdf_page.rect.width,
                                                                     bottom=pdf_page.rect.height)

            pdf_texts += (text_page + '\n')
        return pdf_texts, all_tables


if __name__ == '__main__':
    pdf = "/home/zyl/disk/PharmAI/pharm_ai/intel/data/v1/test_dt_pdfs/6310ee78a81a81d4d4a6de3169ccb40d.pdf"

    print(PDFProcessor.extract_tables_from_non_scanned_pdf(pdf))
