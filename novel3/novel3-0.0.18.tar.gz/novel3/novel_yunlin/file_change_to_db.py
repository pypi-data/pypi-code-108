'''
Author: GanJianWen
Date: 2021-02-26 20:53:59
LastEditors: GanJianWen
LastEditTime: 2021-02-27 18:28:31
QQ: 1727949032
GitHub: https://github.com/1727949032a/
Gitee: https://gitee.com/gan_jian_wen_main
'''
from os import listdir
from os import path
import json


class FileToDatabase:
    def __init__(self, db="sqlite", init=False) -> None:
        module_name = "novel3.novel_yunlin.db.{}".format(db)
        module_meta = __import__(
            module_name, globals(), locals(), [db.capitalize()])
        class_meta = getattr(module_meta, db.capitalize())
        self.database = class_meta()
        init and self.database.set_db_config(first=True)
        self.fp = open("%s/../json/illegal_chapter_name.json" %
                       path.abspath(__file__), 'r', encoding='utf-8')
        self.data_list = json.load(self.fp)

    def get_book_name_from_mysql(self):
        sql = "select book_name from book where latest=0;"
        return self.database.get_datas(sql)

    def init_config(self):
        self.database.set_db_config(first=True)

    def clear_illegal_chapter_name(self, chapter_name):
        for illegal in self.data_list:
            chapter_name = chapter_name.replace(illegal, '')
        return chapter_name

    def insert_book_all_chapters(self):
        book_name_list = self.get_book_name_from_mysql()
        for book_message in book_name_list:
            book_name = book_message[0]
            self.database.log.info("正在插入%s" % book_name)
            book_path = "小说/%s" % book_name
            chapter_list = listdir(book_path)
            if not chapter_list:
                continue
            else:
                chapter_list = sorted(
                    chapter_list, key=lambda x: path.getctime(path.join(book_path, x)))

            for chapter in chapter_list:
                chapter_path = "小说/%s/%s" % (book_name, chapter)
                with open(chapter_path, 'r', encoding='utf-8') as fp:
                    contents = fp.read()
                    fp.close()
                chapter_name = chapter.replace(
                    '.html', '')
                chapter_name = self.clear_illegal_chapter_name(chapter_name)
                sql = "insert into chapter values(NULL,'%s','%s','%s');" % (
                    book_name, chapter_name, contents)
                self.database.query(sql, chapter_name)
            update = "update book set latest=1 where book_name='%s';" % book_name
            self.database.query(update)


if __name__ == "__main__":
    file_to_mysql = FileToDatabase(init=True)
    # file_to_mysql.insert_book_all_chapters()
