

import os

current_directory = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(current_directory, 'hlpl_english_words.db')

import sqlite3
def get(case):
    conn = sqlite3.connect(db)
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    
    if case=='adjective':
       lst=cur.execute("SELECT * FROM en_adj_lst").fetchall()
       return lst 

    if case=='adverb':
       lst=cur.execute("SELECT * FROM en_adv_lst").fetchall()
       return lst
      
    if case=='noun-singular':
       lst=cur.execute("SELECT * FROM en_nouns_s_lst").fetchall()
       return lst
       
    if case=='noun-plural':
       lst=cur.execute("SELECT * FROM en_nouns_p_lst").fetchall()
       return lst

    if case=='verb':
       lst=cur.execute("SELECT * FROM en_verbs_lst").fetchall()
       return lst

    if case=='article':
       lst=cur.execute("SELECT * FROM en_articles_lst").fetchall()
       return lst

    if case=='connection':
       return conn       

