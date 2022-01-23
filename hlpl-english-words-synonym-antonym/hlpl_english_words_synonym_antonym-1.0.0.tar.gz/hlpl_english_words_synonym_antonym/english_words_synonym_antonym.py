
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(current_directory, 'hlpl_english_words_synonym_antonym.db')

import sqlite3
def get():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    lst=cur.execute("SELECT * FROM word_sa").fetchall()
    return lst,conn 


