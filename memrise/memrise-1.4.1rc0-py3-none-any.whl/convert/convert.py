import pandas as pd
import sqlite3 as sql
from pathlib import Path
import os
import re


def concat(mystring: str):
    words = re.findall("\\w+",mystring)
    retStr: str = ""
    for idx in range(len(words)):
        retStr += (words[idx])[0].upper() + (words[idx])[1:]
    return retStr

def convert_sql_to_excel(conn: sql.Connection):
    """File name must be `.xlsx`"""
    # Create a dicrectory output
    Path(f"./output").mkdir(parents=True, exist_ok=True)
    # Open ExcelWriter
    # Open the database
    CMD_COURSE = f"SELECT id,name FROM courses;"
    frame_course = pd.read_sql_query(CMD_COURSE,conn)
    for course in range(frame_course.shape[0]):
        course_id = frame_course['id'][course]
        course_name: str = frame_course['name'][course]
        name = concat(course_name)
        filename = f"./output/{name}.xlsx"
        CMD_LEVELS = f"SELECT id,name FROM levels WHERE course_id = {course_id} ;"
        frame_level = pd.read_sql_query(CMD_LEVELS,conn)
        for idx in range(frame_level.shape[0]):
            # Retrieve all column "id"
            level_id = frame_level['id'][idx]
            CMD_WORDS_IN_LEVEL = f"SELECT word, meaning, sub, IPA FROM words WHERE level_id = {level_id} ;"
            frame_words = pd.read_sql_query(CMD_WORDS_IN_LEVEL,conn)
            if os.path.isfile(filename):
                with pd.ExcelWriter(
                    path = filename,
                    mode = 'a',
                    if_sheet_exists = 'replace',
                    ) as writer:
                    frame_words.to_excel(excel_writer = writer, sheet_name = f"Level {level_id}")
            else:
                with pd.ExcelWriter(
                    path = filename,
                    mode = 'w'
                    ) as writer:
                    frame_words.to_excel(excel_writer = writer, sheet_name = f"Level {level_id}")

if __name__ == "__main__":
    database = "test.db"
    conn = sql.Connection(f"{database}")
    convert_sql_to_excel(conn)
