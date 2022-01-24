import boto3
import tempfile
import logging

import json
import base64
import io

from PIL import Image
import PIL
from botocore.exceptions import ClientError


class PdfGenerator:

    logger = logging.getLogger('pdfgenerator')

    @staticmethod
    def to_png(page):
        page = page.replace("<img class='picCenter' style='width: inherit;' src='data:image/.png;base64,", "")
        page = page.replace("'></img>", "")
        page = base64.b64decode(page)
        return page

    @staticmethod
    def to_pil(page):
        page = PdfGenerator.to_png(page)
        page = io.BytesIO(page)
        page = Image.open(page)
        return page

    @staticmethod
    def process_images(images, title):
        def pages_iterator(images):
            for page in images:
                page = PdfGenerator.to_png(page)
                page = io.BytesIO(page)
                page = Image.open(page)
                page.load()
                yield page

        first = images[0]
        first_as_pil = PdfGenerator.to_pil(first)
        first_as_p = first_as_pil.convert('P')

        spooled_pdf = tempfile.SpooledTemporaryFile()
        first_as_p.save(spooled_pdf, format='pdf', title=title, append_images=pages_iterator(images[1:]), save_all=True)

        spooled_pdf.seek(0)
        return spooled_pdf


    def build_document(self, caseid, decision_type, number):
        number = str(number).zfill(3)
        path_img = f'documents_v2/decision_documents/{caseid}/{decision_type}/{number}.json'

        bucket = 'cloud-eu-central-1-q97dt1m5d4rndek'
        s3 = boto3.client('s3')

        try:
            self.logger.info('Loading from s3://%s/%s', bucket, path_img)
            r = s3.get_object(Bucket=bucket, Key=path_img)
            j = json.load(r['Body'])
            pages = j['d']
            return PdfGenerator.process_images(pages, 'מסמך תולעת המשפט'), r['LastModified']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                self.logger.info('s3://%s/%s not found, trying pdf', bucket, path_img)
            else:
                raise


        path_pdf = f'documents_v2/decision_documents/{caseid}/{decision_type}/{number}.pdf'
        self.logger.info('Loading PDF from s3://%s/%s', bucket, path_pdf)
        r = s3.get_object(Bucket=bucket, Key=path_pdf)
        spooled_pdf = tempfile.SpooledTemporaryFile()
        spooled_pdf.write(r['Body'].read())
        spooled_pdf.seek(0)
        return spooled_pdf, r['LastModified']


if __name__=='__main__':
    pg = PdfGenerator()
    pdf, lastm =pg.build_document('70430305', 'decisions', 0)
    open(r'C:\Users\andy\Desktop\a.pdf', 'wb').write(pdf.read())