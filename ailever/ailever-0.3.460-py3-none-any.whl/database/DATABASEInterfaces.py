

def DB(dbms, verbose=False):
    dbms = dbms.lower()
    if dbms == 'oracle':
        from .oracle import Oracle
        db_aco = Oracle(verbose)
    elif dbms == 'postgresql':
        from .postgresql import PostgreSQL
        db_aco = PostgreSQL(verbose)
    elif dbms == 'mysql':
        from .mysql import MySQL
        db_aco = MySQL(verbose)
    elif dbms == 'sqlite':
        from .sqlite import SQLite
        db_aco = SQLite(verbose)
    else:
        return None
    return db_aco
        
