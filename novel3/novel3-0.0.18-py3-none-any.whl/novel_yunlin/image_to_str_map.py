'''
Author: GanJianWen
Date: 2021-02-22 22:44:07
LastEditors: GanJianWen
LastEditTime: 2021-03-06 00:15:25
QQ: 1727949032
GitHub: https://github.com/1727949032a/
Gitee: https://gitee.com/gan_jian_wen_main
'''

import json
import re
from os.path import abspath
import requests
from os import system
from os import path, makedirs, listdir
from os.path import isdir, join
from sys import exit

from novel3.novel_yunlin.config import Config


class ImageToStr:
    def __init__(self) -> None:
        self.novel_config = Config.read_config()
        self.file_path_list = list()
        self.fp = open('%s/../json/image_str.json' %
                       abspath(__file__), 'r', encoding='utf-8')
        self.data = json.load(self.fp)
        self.DEFAULT_REQUEST_HEADERS = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age = 0',
            'Connection': 'keep-alive',
            'Host': 'www.yulinzhanye.la',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
        }
        self.picture_number = 0

    def ask_url(self, url):
        while True:
            try:
                response = requests.get(
                    url, self.DEFAULT_REQUEST_HEADERS, timeout=3)
                break
            except:
                continue
        return response.content

    def file_path_chapter_htmls(self, base_dir):
        for path in listdir(base_dir):
            file_path = join(base_dir, path)
            if isdir(file_path):
                self.file_path_chapter_htmls(file_path)
            elif file_path.endswith('.txt'):
                self.file_path_list.append(file_path)

    def visit_all_htmls(self):
        novel_path = self.novel_config.get('novel_path')
        self.file_path_chapter_htmls(f'{novel_path}/第一版主')
        count = 0
        for file_path in self.file_path_list:
            count += 1
            if count % 20 == 0:
                system("cls")
            self.get_image_list(file_path)

    def get_image_list(self, file_path):
        domain = self.novel_config.get("novel_domain")
        if not path.exists("toimg"):
            makedirs("toimg")
        num = 0
        fp = open(file_path, 'r', encoding='utf-8')
        print(file_path)
        html = fp.read()
        pattren = re.compile(r'<img src="(.+?)"/>')
        image_list = set(pattren.findall(html))
        # print(len(image_list))
        for image in image_list:
            if "png" not in image:
                continue
            url = f"{domain}/" + image
            # print("url=", url)
            image_name = url.split('/')[-1]
            if image_name not in self.data:
                self.data[image_name] = str()
                num += 1
                self.picture_number += 1
            else:
                continue
            if "style" in image_name:
                print("该图片获取错误")
                continue
            with open('toimg/%s' % image_name, 'wb') as fp:
                fp.write(self.ask_url(url))

            if self.picture_number >= 8:
                exit(0)

    def clear_illegal_str(self, html: str) -> str:
        self.illegal_list = list()
        self.get_illegal_list()
        for illegal in self.illegal_list:
            html = html.replace(illegal, '')
        html = html.replace("<br/>", "\n").replace(">>", "\n")
        html = html.replace(
            '\n\n\n\n', "\n\n").replace(r"'", r"\'").replace("\\\\", "\\")
        return html

    @classmethod
    def get_illegal_list(cls) -> None:
        with open('%s/../json/illegal.json' % abspath(__file__), 'r', encoding='utf-8') as fp:
            cls.illegal_list = json.load(fp)
            fp.close()

    @classmethod
    def add_illegal_str(cls, illegal_str) -> bool:
        cls.get_illegal_list()
        illegal_str not in cls.illegal_list and cls.illegal_list.append(
            illegal_str)
        # print(self.illegal_list)
        cls.save_illegal_str()

    @classmethod
    def save_illegal_str(cls):
        with open('%s/../json/illegal.json' % abspath(__file__), 'w', encoding='utf-8') as fp:
            json.dump(cls.illegal_list, fp, indent=4, ensure_ascii=False)
            fp.close()

    def image_to_str_each_chapter(self, html) -> str:
        if "<img src" in html:
            for key, value in self.data.items():
                replace_str = '<img src="/toimg/data/%s"/>' % key
                html = html.replace(replace_str, value)
        html = self.clear_illegal_str(html)
        html = self.delete_author_date(html)
        return html

    def image_to_str_all_books(self) -> None:
        self.visit_all_htmls()
        for file_path in self.file_path_list:
            fp = open(file_path, 'r', encoding='utf-8')
            html = fp.read()
            html = self.image_to_str_each_chapter(html)
            with open(file_path, 'w', encoding='utf-8') as fp:
                fp.write(html)
                fp.close()
        self.write_all_image_str()

    def delete_author_date(self, html) -> str:
        html = re.sub(r"作者：.+?<br/><br/>", "", html)
        html = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日<br/><br/>", "", html)
        html = re.sub(r"字数：\d{1,6}<br/><br/>", "", html)
        return html

    def write_all_image_str(self) -> None:
        with open('%s/../json/image_str.json' % abspath(__file__), 'w') as fp:
            json.dump(self.data, fp, indent=4)


if __name__ == "__main__":
    demo = ImageToStr()
    demo.add_illegal_str("test")
