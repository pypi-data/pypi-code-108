# encoding: utf-8
"""
@author: zyl
@file: html_processing.py
@time: 2022/1/20 10:32
@desc:
"""
import pandas as pd
import pdfkit


class HtmlProcessor:
    def __init__(self):
        pass

    def run(self):
        self.test()
        pass

    def test(self):
        df = pd.read_excel("/home/zyl/disk/PharmAI/pharm_ai/intel/data/v1/test_gov_purchase.xlsx")
        contents = df['content'].tolist()[0]
        HtmlProcessor.turn_html_content_to_pdf(contents, './data/v1/s.pdf')

    @staticmethod
    def turn_html_content_to_pdf(content, to_pdf='./data/v1/s.pdf'):
        """ 把html文本写入pdf中--
        df = pd.read_excel("/home/zyl/disk/PharmAI/pharm_ai/intel/data/v1/test_gov_purchase.xlsx")
        contents = df['content'].tolist()[0]
        ProcessingHtml.turn_html_content_to_pdf(contents,'./data/v1/s.pdf')
        """
        config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
        content = content.replace('FangSong', 'SimHei')  # 把仿宋体变为黑体，中文字体要变换/或者直接在系统的fonts中添加对应字体
        content = content.replace('宋体', 'SimHei')
        content = content.replace('Simsun', 'SimHei')

        html = '<html><head><meta charset="UTF-8"></head>' \
               '<body><div align="left"><p>%s</p></div></body></html>' % content
        pdfkit.from_string(html, to_pdf, configuration=config)
