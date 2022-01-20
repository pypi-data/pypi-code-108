# from configparser import Error
# import os
# import mysql.connector

# from daybook.adapters.repository import SqlRepository
# from daybook.domain.model import ReadingLog
# from .config import TEST_BOOK, TEST_DATE, TEST_PAGES, TEST_READER_1

# from dotenv import load_dotenv

# load_dotenv(".env.development")

# MYSQL_HOST = os.environ.get("MYSQL_HOST")
# MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
# MYSQL_USER = os.environ.get("MYSQL_USER")
# MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")


# class TestMySqlRepository:
#     @classmethod
#     def setup_class(self):
#         self.cnx = mysql.connector.connect(
#             user=MYSQL_USER,
#             password=MYSQL_PASSWORD,
#             host=MYSQL_HOST,
#             port=3306,
#             database=MYSQL_DATABASE,
#         )

#     @classmethod
#     def teardown_class(self):
#         if self.cnx is not None and self.cnx.is_connected():
#             self.cnx.close()

#     def test_add(self):
#         reading_log = ReadingLog(TEST_READER_1)
#         with self.cnx.cursor(buffered=True) as cursor:
#             reading_log.add_entry(TEST_DATE, TEST_BOOK, TEST_PAGES)
#             repo = SqlRepository(cursor)
#             repo.add(reading_log)
#             self.cnx.commit()
#             cursor.execute(f"SELECT * FROM reading_log WHERE reader = '{TEST_READER_1}';")
#             reader_name = cursor.fetchone()[1]
#             self.cnx.commit()
#         assert TEST_READER_1 == reader_name

#     def test_get(self):
#         repo = SqlRepository(self.cnx)
#         reading_log = repo.get(TEST_READER_1)
#         assert reading_log.reader == TEST_READER_1
