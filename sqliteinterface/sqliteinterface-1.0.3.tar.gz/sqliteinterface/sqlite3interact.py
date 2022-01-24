'''
Created on 19. 1. 2022

@author: ppavlu

Module to collect interactions with a SQLite3 database 
Initial purpose - for storing data ead from Loxone home controller
'''

import sqlite3
import os

def DB_Connect(fnametext,tname,colnames,coltypes,verb): 
#DB COnnection to file, needs more exception handling
    if not os.path.isfile(fnametext):
        if verb:
            print("Opening a new database file: ",fnametext)
    con=sqlite3.connect(fnametext)
    res=DB_Action(con, "pragma table_info("+tname+");",verb)
    if (res[1] != []): #table exists
        if verb:
            print("Table ",tname," exists in database, OK.")
        #Here we might need to make checks of the database - table and its structure
        #for now we assume that if it exists, then it is OK
    else: #table does not exist
        fstr=""
        for i in range (0,len(colnames)):
            if i>0:
                fstr=fstr+","
            fstr=fstr+colnames[i]+" "+coltypes[i]
        cmd="create table "+tname+" ("+fstr+");"
        res=DB_Action(con, cmd,verb)
        if (res[0] != 0):
            print("Failed to create table ", tname)
    return con


def DB_Action(con,command,verb):
# con is the database object - connection established
# command is the SQL to be executed in the DB
# returns a set of exit code (0 is OK, 1 is error) and command output
    if verb:
        print ("Executing command: ",command)
    try:
        cur=con.cursor()
        cur.execute(command)
    except (sqlite3.DatabaseError,sqlite3.ProgrammingError):
        print ("Wrong SQL statement")
        return (1,[])
    return (0,cur.fetchall())

def DB_Close(con):
    con.close()

if __name__ == '__main__':
    pass