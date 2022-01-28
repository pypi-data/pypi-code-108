#Insieme di funzioni per interagire con SQLite

import sqlite3
import time
import pandas as pd
import request

KEY = "518e72a11de080028921e78aba2a102c"
URL_KEY = "&api_key=" + KEY + "&file_type=json"
URL_BASE = "https://api.stlouisfed.org/fred/"
DB = "./database.db"

def connect_db(db_file):
    
    connection = None
    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        return connection
    
def create_db(db_file):
    
    connection = connect_db(db_file)
    cursor = connection.cursor()
    
    #Tabella delle categorie scaricate
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS categories
       ([id] TEXT PRIMARY KEY, [name] TEXT, [parent_id] TEXT)
       ''')
    
    #Tabella delle serie scaricate e/o analizzate
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS seriess
       ([id] TEXT PRIMARY KEY, [title] TEXT)
       ''')
        
    #Tabella con le osservabili delle serie scaricate e/o analizzate
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS observations
       ([date] TEXT, [id] TEXT, [value] TEXT, PRIMARY KEY (date, id))
       ''')
        
    #Tabella con l’elenco delle serie scaricate
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS seriess_downloaded
       ([id] TEXT PRIMARY KEY, [title] TEXT)
       ''')
        
    connection.commit()
    connection.close()

def insert_db(db_file, id, type, update):

    json = request.get(URL_BASE, URL_KEY, type, id)
    if json == -1:
        
        print("Wrong request!")
        return -1
        
    if type == "category_children":
          
        categories = json.json()["categories"]
        lenght = len(categories)
                
        query_check = ''' SELECT count(*) FROM categories WHERE id = (?) '''
        query_update = ''' UPDATE categories SET name = (?), parent_id = (?) WHERE id = (?) '''
        query = ''' INSERT INTO categories (id, name, parent_id) VALUES (?,?,?) '''
    
    elif type == "observation":
        
        observations = json.json()["observations"]
        lenght = len(observations)
        
        query_check = ''' SELECT count(*) FROM observations WHERE date = (?) AND id = (?) '''
        query_update = ''' UPDATE observations SET value = (?) WHERE date = (?) AND id = (?) '''
        query = ''' INSERT INTO observations (date, id, value) VALUES (?,?,?) '''

    elif type == "series":
        
        series = json.json()["seriess"]
        lenght = len(series)
        
        query_check = ''' SELECT count(*) FROM seriess WHERE id = (?) '''
        query_download = ''' INSERT INTO seriess_downloaded (id, title) VALUES (?,?) ''' 
        query_update = ''' UPDATE seriess SET title = (?) WHERE id = (?) '''
        query = ''' INSERT INTO seriess (id, title) VALUES (?,?) '''
        
    else:
        
        print("Wrong param!")
        return -1
        
    if lenght == 0: return 0
        
    connection = connect_db(db_file)
    cursor = connection.cursor()
        
    for index in range(lenght):
        
        if type == "category_children":
            
            category = categories[index]

            #controlla se (id) è già presente
            params = category["id"],
            cursor.execute(query_check, params)
            check = cursor.fetchone()[0]
    
            #se (id) presente e si vuole aggiornare, allora viene aggiornato il valore
            if check != 0 and update == True:
                
                params = category["name"], category["parent_id"], id
                cursor.execute(query_update, params)
                continue
            
            #se tupla non presente, la si inserisce
            elif check == 0:
                
                params = category["id"], category["name"], category["parent_id"]
                cursor.execute(query, params)
            
        if type == "observation":
        
            observation = observations[index]

            #controlla se (date,id) è già presente
            params = observation["date"], id
            cursor.execute(query_check, params)
            check = cursor.fetchone()[0]
    
            #se (date,id) presente e si vuole aggiornare, allora viene aggiornato il valore
            if check != 0 and update == True:
                
                params = observation["value"], observation["date"], id
                cursor.execute(query_update, params)
                continue
            
            #se tupla non presente, la si inserisce
            elif check == 0:
                
                params = observation["date"], id, observation["value"]
                cursor.execute(query, params)

        elif type == "series":
            
            serie = series[index]
            
            #controlla se id della serie già presente
            params = series[index]["id"],
            cursor.execute(query_check, params)            
            check = cursor.fetchone()[0]

            #se id presente e si vuole aggiornare il dato, si aggionrato la tupla
            if check != 0 and update == True:
                
                params = series[index]["title"], series[index]["id"]
                cursor.execute(query_update, params)
                continue
             
            #se tupla non presente, la si inserisce
            elif check == 0:

                params = series[index]["id"], series[index]["title"]
                cursor.execute(query, params)
                cursor.execute(query_download, params)
                        
        connection.commit()
             
    connection.close()

def get_db(db_file, type, id):
    
    connection = connect_db(db_file)
    cursor = connection.cursor()
    
    if type == "category_children":
        
        cursor.execute(''' SELECT c.id, c.name, c.parent_id FROM categories c ORDER BY c.parent_id ASC ''')
        df = pd.DataFrame(cursor.fetchall(), columns=['id','name','parent_id'])

    elif type == "seriess":
        
        cursor.execute(''' SELECT s.id, s.title FROM seriess s ''')
        df = pd.DataFrame(cursor.fetchall(), columns=['id','title'])
        
    elif type == "seriess_downloaded":
        
        cursor.execute(''' SELECT s.id, s.title FROM seriess_downloaded s ''')
        df = pd.DataFrame(cursor.fetchall(), columns=['id','title'])
    
    elif type == "observations":
        
        if id is None:
        
            cursor.execute(''' SELECT o.date, o.id, o.value FROM observations o ''')
            
        else:
            
            query = ''' SELECT o.date, o.id, o.value FROM observations o WHERE o.id = (?) '''
            params = id,
            cursor.execute(query, params)
            
        df = pd.DataFrame(cursor.fetchall(), columns=['date', 'id', 'value'])

    else:
        
        connection.close()
        print("Wrong param!")
        return -1
    
    connection.close()
    return df

def download_insert_tree_category(db_file, id, type, update, array):
    
    #per evitare un numero eccessivo di richieste in poco tempo (soprattutto se id = 0)
    time.sleep(.5)
    ret = insert_db(db_file, id, type, update)
    
    #si è giunti fino alle foglie dell'albero, quindi si ritorna
    if ret == 0: return array

    connection = connect_db(db_file)
    cursor = connection.cursor()
    
    #si selezionano tutti gli id, dei figli appena scaricati        
    query = ''' SELECT c.id FROM categories c WHERE c.parent_id = (?) '''
    params = id,
    cursor.execute(query, params)
    df = pd.DataFrame(cursor.fetchall(), columns=['id'])
    
    for index in range(len(df)):
              
        value = df.iloc[index]['id']
        array.append(value)
        array = download_insert_tree_category(DB, value, "category_children", False, array)
    
    connection.close()
    return array