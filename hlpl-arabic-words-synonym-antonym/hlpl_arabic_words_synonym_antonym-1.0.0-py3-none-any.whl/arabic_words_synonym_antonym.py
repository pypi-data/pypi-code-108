

import os
current_directory = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(current_directory, 'hlpl_arabic_words_synonym_antonym.db')

import sqlite3
def get():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    lst_1=cur.execute("SELECT * FROM noun_sa").fetchall()
    lst_2=cur.execute("SELECT * FROM verb_sa").fetchall()
    return lst_1,lst_2,conn

