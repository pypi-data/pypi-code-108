
#####################################################################
#
# log_traceid:::datetime:::context:::msg
#
# s_log.py
#
# Project   : SAPIADAPTER
# Author(s) : Zafar Iqbal < zaf@sparc.space >
# Copyright : (C) 2022 SPARC PC < https://sparc.space/ >
#
# All rights reserved. No warranty, explicit or implicit, provided.
# SPARC PC is and remains the owner of all titles, rights
# and interests in the Software.
#
# FIXME TODO - log rotation/retention to not overflow disk space
#
#####################################################################

import os
import json
from datetime import datetime
#import uuid
#import hashlib
from inspect import currentframe , getframeinfo
from . import s_config , s_util

#####################################################################

log_filepath = False
log_traceid = False

#####################################################################

def init( ) :

    #if(not s_config.key_is_yes("log")): return(False)

    global log_traceid
    global log_filepath

    if( log_traceid != False ) : return

    log_workspacedir = s_config.get_key( "sys/workspacedir" , "/tmp/sapiadapter")

    if( not log_workspacedir ) : return

    os.makedirs( log_workspacedir , exist_ok = True )

    # Add trailing slash
    log_filepath = os.path.join( log_workspacedir , "" ) + "main.log" 

    log_traceid = s_util.uhash( "TRI" )

#####################################################################

def get_traceid( ) :
    return( log_traceid )

#####################################################################

def default_json( t ) :
    return f'{t}'

#####################################################################

def write( msg_raw ) :

    #if not init( ): return
    init( )
    if( s_config.key_is_no( "sys/log" ) ) : return

    msg = msg_raw

    if( msg == None ) : msg = "!NONE!"
    
    if( isinstance( msg , list ) ) :
        msg = ",".join( map( str , msg ) )
    
    if( isinstance( msg , dict ) ) :
        # FIXME TODO use util json note numpy stuff
        msg = json.dumps( msg , default = default_json , indent=4, sort_keys=True)

    if( isinstance( msg , ( int , float , bool ) ) ) :
        msg = str( msg )


    cf = currentframe( ).f_back

    frameinfo = getframeinfo( cf )

    functionname = frameinfo[ 2 ]

    filename = frameinfo.filename

    context = filename + "," + functionname + "," + str( cf.f_lineno )

    # msg = "-:::" + log_traceid + ":::" + datetime.now( ).strftime( "%Y_%m_%d-%H_%M_%S" ) + ":::" + context + ":::" + msg
    msg = "-:::" + log_traceid + ":::" + s_util.time_getisoformat( ) + ":::" + context + ":::" + msg
    with open( log_filepath , "a+" , 1 ) as log_file :
        log_file.write( msg + "\n" )

#####################################################################

def flush( ) :
    if os.path.isfile( log_filepath ) :
        os.remove( log_filepath )




