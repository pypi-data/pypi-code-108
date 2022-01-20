
#####################################################################
#
# s_db.py
#
# Project   : SAPIADAPTER
# Author(s) : Zafar Iqbal < zaf@sparc.space >
# Copyright : (C) 2022 SPARC PC < https://sparc.space/ >
#
# All rights reserved. No warranty, explicit or implicit, provided.
# SPARC PC is and remains the owner of all titles, rights
# and interests in the Software.
#
#####################################################################

import os
import sys
import json
import time
import platform
#import datetime
import hashlib
import sqlite3

from . import s_log , s_config , s_util

#####################################################################

filepath = False
db_con = False

#####################################################################

def commitclose( ) :
    
    global db_con

    if( db_con != False ) :
        db_con.commit( )
        db_con.close( )
        db_con = False 

def setup( ) :

    global filepath

    #s_log.write(sys.argv)
    #if(len(sys.argv)==3 and sys.argv[0]=="_sapi.py"):
    #    filepath=sys.argv[1]
    #    db_con_setup( )
    #    s_log.write("db filepath " + filepath)
    #    return

    ################################################################

    if( filepath != False ) :
        flush( )
        return( True )

    s_log.write( "db setup" )

    ################################################################

    filepath_setup( )

    ################################################################

    db_con_setup( )

    ################################################################

    if( not os.path.isfile( filepath ) ) :
        s_log.write( "False filepath isfile" ) 
        return( False )

    ################################################################

    init_schema( )
    init_data( )
    
    ################################################################

    return( True )

def flush( ) :

    table_truncate( "files" ) 
    table_truncate( "env" ) 
    table_truncate( "stdio" ) 
    table_truncate( "args" ) 
    table_truncate( "stacks" ) 
    table_truncate( "meta" ) 
    table_truncate( "templates" ) 


def init_data( ) :
# FIXME TODO add host environment vars e.g. hostname/machine id etc.
    sys_create( "ver_db" , "1.0" )
    sys_create( "ver_sapi" , s_config.get_key( "/config/version" ) )
    sys_create( "serial" , "ODS042e1919c5bd8f41cd8e1a2b8e455dd8f6fb00df0c3916d1137047a7aafc4c42" )
    sys_create( "motto" , "HORAS NON NUMERO NISI SERENAS" )
    sys_create( "rev" , 1 )
    #sys_create( "sys_platform" , sys.platform )
    #sys_create( "sys_version" , sys.version )
    sys_create( "traceid" , s_log.get_traceid( ) )
    sys_create( "time_isoformat" , s_util.time_getisoformat( ) )
    sys_create( "tcreate" , time.time( ) )
    sys_create( "platform_uname" , platform.uname( ) )
    sys_create( "python_version" , platform.python_version( ) )

    sys_create( "config_dbpassthru" , s_config.get_key( "db/passthru" ) )

    #s_log.write(sys_read("time_isoformat"))

def fdelete( ) :

    commitclose( )

    if( os.path.isfile( filepath ) ) :
        os.remove( filepath )

def file_contents( ) :

    commitclose( )

    if not os.path.isfile( filepath ) :
        s_log.write( filepath + " NOT exists!" )
        return( False )

    with open( filepath , mode = "rb" ) as file : 
        db_filecontents = file.read( )

    db_con_setup( )

    return( db_filecontents )


def blob_set( d ) :
    blob = s_util.decompress( d )
    rewrite( blob )

def blob_get( ) :
    db_filecontents = file_contents( )
    blob = s_util.compress( db_filecontents )
    return( blob )

def rewrite( payload ) :

    #rev = 1
    #if( db_con_check( ) ) :
    #    rev = sys_read( "rev" ) + 1

    commitclose( )

    if( len( payload ) == 0 ) :
        s_log.write( "ERROR payload empty??")

    with open( filepath , "wb" ) as file:
        file.write( payload )

    db_con_setup( )

    ################################################################

    ver_sapi = sys_read( "ver_sapi" )
    ver_db = sys_read( "ver_db" )

    if( ver_sapi != s_config.get_key( "/config/version" ) ) :
        #s_log.write( "WARNING,VER_SAPI MISMATCH," + ver_sapi + "!=" + s_config.get_key( "/config/version" ) + "," + ver_db )
        s_log.write( "WARNING, VERSION MISMATCH," )


    #sys_update("rev",rev)
    #s_log.write("REV rewrite "+str(rev))

def db_con_setup( ) :

    global db_con

    if( db_con != False ) : return

    db_con = sqlite3.connect( filepath )
    #db_con.row_factory = sqlite3.Row
    db_con.row_factory = lambda C , R : { c[ 0 ] : R[ i ] for i , c in enumerate( C.description ) }

    #s_log.write( "OK db_con_setup" )

def db_con_check( ) :
    global db_con
    try :
        db_con.cursor( )
        return( True )
    except Exception as ex :
        return( False )

#####################################################################


def filepath_get( ) :
    return( filepath )

def filepath_setup( ) :

    global filepath

    if( filepath != False ) :
        return

    ################################################################

    dbworkspacedir = os.path.join( s_config.get_key( "sys/workspacedir" , "/tmp/sapiadapter" ) + "/db" , "" )

    os.makedirs( dbworkspacedir , exist_ok = True )

    filepath = dbworkspacedir + s_config.get_key( "/config/session" ) + ".db" 

#####################################################################

def sql_execute( sql ) :
    #s_log.write( sql )
    cur = db_con.cursor( )
    cur.execute( sql )
    db_con.commit( )

def sql_execute_parameters( sql , params_tuple ) :

    cur = db_con.cursor( )
    cur.execute( sql , params_tuple )
    db_con.commit( )

def sql_execute_fetchall( sql ) :
    cur = db_con.cursor( )
    cur.execute( sql )
    rows = cur.fetchall( )
    return( rows )

def sql_execute_fetchone( sql ) :
    cur = db_con.cursor( )
    cur.execute( sql )
    row = cur.fetchone( )
    if( not row ) : return( False )
    return( row )

def table_readall( t , extra = "" ) :
    sql = "SELECT * FROM " + t + " " + extra
    rows = sql_execute_fetchall( sql )
    return( rows )

def table_truncate( t , extra = "" ) :
    sql = "DELETE from " + t + " " + extra
    sql_execute( sql )

def table_rowcount( t , extra = "") :
    sql = "SELECT COUNT(*) as count FROM " + t + " " + extra
    row = sql_execute_fetchone( sql )
    return( row[ "count" ] )

def tablerow_exists( t , extra = "" ) :
    row_count = table_rowcount( t , extra ) 
    if(row_count>0): return(True)
    return(False)


#####################################################################

def init_schema( ) :

    sql_execute( "CREATE TABLE sys ( sn text UNIQUE , sv text )" )
    sql_execute( "CREATE INDEX index_sys ON sys ( sn )" )

    ################################################################

    sql_execute( "CREATE TABLE files ( fp text UNIQUE , fc blob , fs integer , fh text )" )
    sql_execute( "CREATE INDEX index_files ON files ( fp )" )

    ################################################################

    sql_execute( "CREATE TABLE env ( eid integer PRIMARY KEY AUTOINCREMENT , en text UNIQUE , ev text )" )
    sql_execute( "CREATE INDEX index_env ON env ( eid , en )" )

    ################################################################

    sql_execute( "CREATE TABLE stdio ( sid integer PRIMARY KEY AUTOINCREMENT , sk integer , sv text )" )
    sql_execute( "CREATE INDEX index_stdio ON stdio ( sid , sk )" )

    ################################################################

    sql_execute( "CREATE TABLE args ( aid integer PRIMARY KEY AUTOINCREMENT , av text )" )
    sql_execute( "CREATE INDEX index_args ON args ( aid )" )

    ################################################################

    sql_execute( "CREATE TABLE stacks ( sid integer PRIMARY KEY AUTOINCREMENT , sk integer , sv text )" )
    sql_execute( "CREATE INDEX index_stacks ON stacks ( sid , sk )" )

    ################################################################

    sql_execute( "CREATE TABLE meta ( mn text UNIQUE , mv text )" )
    sql_execute( "CREATE INDEX index_meta ON meta ( mn )" )

    ################################################################

    sql_execute( "CREATE TABLE templates ( tid integer PRIMARY KEY AUTOINCREMENT , tp text , tk text , tv text )" )
    sql_execute( "CREATE INDEX index_templates ON templates ( tid , tp )" )

#####################################################################

def sys_create( sn , sv_in ) :

    sv = s_util.json_encode( sv_in )

    sql = "INSERT INTO sys( sn , sv ) VALUES ( ? , ? )"
    data = ( sn , sv )
    sql_execute_parameters( sql , data )
    return( True )

def sys_count( ) :
    count = table_rowcount( "sys" )
    return( count )

def sys_read( sn ) :

    sql = "SELECT * FROM sys where sn='" + sn + "' limit 1"
    row = sql_execute_fetchone( sql )
    if( not row ) : return( False )
    return( json.loads( row[ "sv" ] )  )

def sys_readall( ) :
    rows = table_readall( "sys" )
    return( rows )

def sys_update( sn , sv_in ) :
    sv = s_util.json_encode( sv_in )
    sql = "UPDATE sys SET sv=? where sn=?"
    data = ( sv , sn )
    sql_execute_parameters( sql , data )

def sys_delete( sn ) :

    sql = "DELETE FROM sys where sn='" + sn + "'"
    sql_execute( sql )
    return( True )

def sys_deleteall( ) :
    table_truncate( "sys" )

def sys_rev_inc( ) :
    newrev = sys_read( "rev" ) + 1
    sys_update( "rev" , newrev )

####################################################################

def stacks_create( sv_data , sk = 0 ) :

    sv = s_util.json_encode( sv_data )

    sql = "INSERT INTO stacks ( sid , sk,sv ) VALUES ( ? , ? , ? )"
    data = ( None , sk,sv )

    sql_execute_parameters( sql , data )
    return( True )

def stacks_count( sk = 0 ) :

    extra = "where sk=" + str( sk )
    count = table_rowcount( "stacks" , extra )
    return( count )

def stacks_read( sk = 0 ) :

    sql = "SELECT * FROM stacks where sk=" + str( sk ) + " order by sid desc" 
    rows = sql_execute_fetchall( sql )
    return( rows )

def stacks_readall( ) :
    # FIXME TODO ORDER by sid!
    rows = table_readall( "stacks" )
    return( rows )

def stacks_update( sid , sk , sv_data ) :
    sv = s_util.json_encode( sv_data )
    sql = "UPDATE stacks SET sk=? , sv=? where sid=?"
    data = ( sk , sv , sid )
    sql_execute_parameters( sql , data )

def stacks_delete( sk = 0 ) :
    sql = "DELETE FROM stacks where sk=" + str( sk ) 
    sql_execute( sql )
    return( True )

def stacks_deleteall( ) :
    table_truncate( "stacks" )
    return(True)

def stacks_pop( sk = 0 ) :

    sql = "SELECT * FROM stacks where sk=" + str( sk ) + " order by sid desc limit 1" 
    rows = sql_execute_fetchall( sql )

    if( len( rows ) != 1 ) :
        return( False )

    row = rows[ 0 ]
   
    sid = row[ "sid" ]
    sv_dict = json.loads( row[ "sv" ] )

    sql = "DELETE FROM stacks where sid=" + str( sid ) 
    sql_execute( sql )

    return( sv_dict )    


#####################################################################

def env_create( en , ev ) :

    sql = "INSERT INTO env ( eid , en , ev ) VALUES ( null , ? , ? )"
    data = ( en , ev )
    sql_execute_parameters( sql , data )
    return(True)

def env_count( ) :
    count = table_rowcount( "env" )
    return( count )

def env_read( en ) :

    sql = "SELECT * FROM env where en='" + en + "' limit 1"
    row = sql_execute_fetchone( sql )
    return( row )

def env_readall( ) :
    rows = table_readall( "env" , "order by eid asc")
    return( rows )

def env_update( en , ev ) :
    sql = "UPDATE env SET ev=? where en=?"
    data = ( ev , en )
    sql_execute_parameters( sql , data )

def env_delete( en ) :

    sql = "DELETE FROM env where en='" + en + "'"
    sql_execute( sql )
    return( True )

def env_deleteall( ) :
    table_truncate( "env" )

#####################################################################

def meta_create( mn , mv_in ) :

    # FIXME TODO something better?
    meta_delete( mn )

    mv = s_util.json_encode( mv_in )

    sql = "INSERT INTO meta ( mn , mv ) VALUES ( ? , ? )"
    data = ( mn , mv )
    sql_execute_parameters( sql , data )
    return(True)

def meta_count( ) :
    count = table_rowcount( "meta" )
    return( count )


def meta_read( mn ) :

    sql = "SELECT * FROM meta where mn='" + mn + "' limit 1"
    row = sql_execute_fetchone( sql )
    if( not row ) : return( False )
    return( json.loads( row[ "mv" ] )  )

def meta_readall( ) :
    rows = table_readall( "meta" )
    return( rows )

def meta_update( mn , mv_in ) :
    mv = s_util.json_encode( mv_in )
    sql = "UPDATE meta SET mv=? where mn=?"
    data = ( mv , mn )
    sql_execute_parameters( sql , data )

def meta_delete( mn ) :

    sql = "DELETE FROM meta where mn='" + mn + "'"
    sql_execute( sql )
    return( True )

def meta_deleteall( ) :
    table_truncate( "meta" )

def meta_createorupdate( mn , mv ) :
    t = meta_read( mn )
    if t :
        meta_update( mn , mv )
    else :
        meta_create( mn , mv )


####################################################################

def args_create( av ) :

    sql = "INSERT INTO args ( aid , av ) VALUES ( ? , ? )"
    data = ( None , av )
    sql_execute_parameters( sql , data )
    return( True )

def args_count( ) :
    count = table_rowcount( "args" )
    return( count )

def args_read( aid ) :

    sql = "SELECT * FROM args where aid=" + aid + " limit 1"
    row = sql_execute_fetchone( sql )
    return( row )

def args_readall( ) :
    rows = table_readall( "args" , "order by aid asc")
    return( rows )

def args_update( aid , av ) :
    sql = "UPDATE args SET av=? where aid=?"
    data = ( av , aid )
    sql_execute_parameters( sql , data )

def args_delete( aid ) :

    sql = "DELETE FROM args where aid=" + aid 
    sql_execute( sql )
    return( True )

def args_deleteall( ) :
    table_truncate( "args" )

####################################################################

# stdin 0 , stdout 1 , stderr 2
def stdio_create( sk , sv ) :
    sql = "INSERT INTO stdio ( sid , sk , sv ) VALUES ( null , ? , ? )"
    data = ( sk , sv )
    sql_execute_parameters( sql , data )
    return( True )

def stdio_count( sk ) :
    count = table_rowcount( "stdio" , "where sk=" + str( sk ) )
    return( count )

def stdio_read( sk ) :
    sql = "SELECT * FROM stdio where sk=" + str( sk ) + " order by sid asc" 
    rows = sql_execute_fetchall( sql )
    return( rows )

def stdio_readformatted( sk ) :
    rows = stdio_read( sk )
    buff = ""
    for r in rows:
        #buff = buff + str( r["sv"],"utf-8")+"\n"
        buff = buff + r["sv"]+"\n"
    return( buff )

def stdio_readall( ) :
    rows = table_readall( "stdio" )
    return( rows )

def stdio_update( sid , sk , sv ) :
    sql = "UPDATE stdio SET sk=? , sv=? where sid=?"
    data = ( sk , sv , sid )
    sql_execute_parameters( sql , data )

def stdio_delete( sk = 0 ) :

    sql = "DELETE FROM stdio where sk = " + str( sk ) 
    sql_execute( sql )

    return( True )    

def stdio_deleteall( ) :
    table_truncate( "stdio" )

def stdio_has_stderr( ) :

    if( stdio_count( 2 ) > 0 ) :
        return( True )

    return( False )

def stdio_get_stderr( ) :
    return( stdio_readformatted( 2 ) )

def stdio_get_stdout( ) :
    return( stdio_readformatted( 1 ) )

####################################################################

def files_create( fp ) :

    # FIXME TODO have some restriction paths allowed - this breaks when creating UID directories for work spaces
    # FIXME TODO add tests for this...
    #if( s_util.pathnotallowed( fp ) ) : return( False )

    ####################################################################

    if not os.path.isfile( fp ) :
        s_log.write( fp + " NOT found!" )
        return( False )

    fs = os.path.getsize( fp )

    with open( fp , mode = "rb" ) as file : 
        fc = file.read( )

    fh = hashlib.md5( fc ).hexdigest( )

    ####################################################################

    sql = "INSERT INTO files ( fp , fc , fs , fh ) VALUES (?, ?, ?, ?)"
    data_tuple = ( fp , fc , fs , fh )

    sql_execute_parameters( sql , data_tuple )

    return( True )

def files_count( ) :
    count = table_rowcount( "files" )
    return( count )

def files_read( fp ) :

    sql =  "SELECT * FROM files where fp='" + fp + "' limit 1" 
    row = sql_execute_fetchone( sql )
    return( row )

def files_readall( ) :
    rows = table_readall( "files" )
    return( rows )

# FIXME TODO def files_update !!!
# Delete current path and create a new one?!?!?!
def files_update( fp ) :
    files_delete( fp ) 
    return( files_create( fp ) )

def files_delete( fp ) :

    sql = "DELETE FROM files where fp='" + fp + "'"
    sql_execute( sql )

    return( True )  

def files_deleteall( ) :
    table_truncate( "files" )

def files_dict2json( fp , fdict ) :

    #if( s_util.pathnotallowed( fp ) ) : return( False )

    fc = s_util.json_encode( fdict )

    fs = len( fc )
    fh = hashlib.md5( fc.encode( "utf-8" ) ).hexdigest( )

    sql = "INSERT INTO files ( fp , fc , fs , fh ) VALUES (?, ?, ?, ?)"
    data_tuple = ( fp , fc , fs , fh )
    sql_execute_parameters( sql , data_tuple )

    return( True )

def files_getcontent( fp ) :
    f = files_read( fp )
    if not f:
        s_log.write( "False files_getcontent" )
        return( False )
    return( f[ "fc" ] )

def files_write( fp ) :
    with open( fp , "w" , 1 ) as f :
        f.write( files_getcontent( fp ) )


########################
'''
def files_defmeta_set( data ) :

    files_delete( "./local_defmeta_5800b137d.json" )

    flag = files_dict2json( "./local_defmeta_5800b137d.json" , data )
    if not flag :
        s_log.write( "False files_defmeta_set" )
        return( False )

    return( True )

def files_defmeta_get( ) :
    f = files_read( "./local_defmeta_5800b137d.json" )
    if not f :
        s_log.write( "False files_defmeta_set files_read" )
        return( False )
    d = json.loads( f[ "fc" ] )
    return( d )

def files_defmeta_write( ) :
    files_write( "./local_defmeta_5800b137d.json" )
########################
def files_defdata_set( data ) :

    files_delete( "./local_defdata_5800b137d.json" )

    flag = files_dict2json( "./local_defdata_5800b137d.json" , data )
    if not flag :
        s_log.write( "False files_defdata_set" )
        return( False )

    return( True )

def files_defdata_get( ) :
    f = files_read( "./local_defdata_5800b137d.json" )
    if not f :
        s_log.write( "False files_defdata_get files_read" )
        return( False )
    d = json.loads( f[ "fc" ] )
    return( d )

def files_defdata_write( ) :
    files_write( "./local_defdata_5800b137d.json" )
'''

####################################################################

def templates_create( tp , tk , tv ) :
    if( s_util.pathnotallowed( tp ) ) : return( False )
    sql = "INSERT INTO templates ( tp,tk,tv) VALUES ( ? , ? , ? )"
    data = ( tp , tk , tv )
    sql_execute_parameters( sql , data )
    return(True)

def templates_count( ) :
    count = table_rowcount( "templates" )
    return( count )

def templates_read( tp ) :
    sql = "SELECT * FROM templates where tp='" + tp + "' order by tid asc" 
    rows = sql_execute_fetchall( sql )
    return( rows ) 

def templates_readall( ) :
    rows = table_readall( "templates" )
    return( rows )    

def templates_update( tp , tk , tv ) :
    sql = "UPDATE templates SET tk=? , tv=? where tp=?"
    data = ( tk , tv , tp )
    sql_execute_parameters( sql , data )

def templates_delete( tp ) :

    sql = "DELETE FROM templates where tp='" + tp + "'"
    sql_execute( sql )
    return( True )

def templates_deleteall( ) :
    table_truncate( "templates" )

