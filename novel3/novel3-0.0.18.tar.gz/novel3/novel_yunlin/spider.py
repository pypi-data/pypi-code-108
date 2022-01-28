from novel3.novel_yunlin.image_to_str_map import ImageToStr
from novel3.novel_yunlin.yun_lin_zhan_ye_scrapy import YuLinZhanYeScrapy
from novel3.novel_yunlin.file_change_to_db import FileToDatabase
from os import system
from os.path import abspath
import re
import json


def novel_content_modify(novel_path: str):
    with open(novel_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    content = re.sub(r'作者[\s\S]+?字数：\d{1,14}\n', '', content)
    lines = content.splitlines()

    total_content = str()
    for line in lines:
        total_content += line
        if len(line) > 2 and line[-2] == "。":
            total_content += "\n\n"
    print(total_content)


def spider_run(db="sqlite"):
    choose = 1
    while choose > 0:
        system("cls")
        print("1、爬取小说")
        print("2、图片转文字")
        print("3、将数据插入数据库")
        print("0、退出")
        choose = int(input("选择:"))
        if choose == 1:
            spider = YuLinZhanYeScrapy(db)
            spider.main()
        if choose == 2:
            demo = ImageToStr()
            demo.image_to_str_all_books()
        if choose == 3:
            demo = FileToDatabase(db)
            demo.insert_book_all_chapters()


def set_novel_path(file_path=str()):
    with open(f"{abspath(__file__)}/../config/novel.json", "w", encoding="utf-8") as fp:
        json.dump({"novel_path": file_path}, fp, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    spider_run()
