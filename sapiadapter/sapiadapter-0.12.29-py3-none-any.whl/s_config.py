
#####################################################################
#
# s_confg.py
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

#####################################################################

from . import get_version
from . import s_log  , s_util

#####################################################################

config = { }
config_alt = { }

ready = False

#####################################################################

def setup( config_user = None ) :

    global ready

    flag = init( config_user ) 

    if not flag :
        s_log.write( "False init!" )
        return( flag )


    preprocess( ) 

    ready = True

    s_log.write( get_config( ) )
    s_log.write( get_config_alt( ) )

    return( True )


def preprocess( ) :
    handle_key_fromcontainer( )
    unpack_key( )
    handle_sslverify_fornumericip( )
    handle_key_public( )
    checkup_workspacedir( )


def get_key( config_key , default_val = None ) :

    #    config[ "/config/init/path" ] = config_path
    #    config[ "/config/init/path_time" ] = os.path.getmtime( config_path )
    # config[ "/config/cwd" ]
    if( "/config/init/path_time" in config ) :
        cd = config[ "/config/cwd" ]
        cip = config[ "/config/init/path" ]
        cipt = config[ "/config/init/path_time" ]

        cfp = cd + "/" + cip

    if( config_key in config_alt ) :
        #s_log.write_msg("GET KEY FOUND")
        if config_alt[ config_key ] != None :
            return config_alt[ config_key ]
 

    #s_log.write_msg("GET KEY "+config_key)
    if( config_key in config ) :
        #s_log.write_msg("GET KEY FOUND")
        if config[ config_key ] != None :
            return config[ config_key ]
            
    #s_log.write_msg("GET KEY NULL")
    return default_val



def checkup_workspacedir( ) :

    wd = get_key( "sys/workspacedir" )
    
    if not wd :
        set_key( "sys/workspacedir" , "/tmp/sapiadapter" )

def handle_key_fromcontainer( ) :
    

    if( get_key( "endpoint/key" ) ) :
        return

    if not "_CONTAINER_LOCAL_CONFIGENDPOINTKEY" in os.environ : return

    endpoint_key = os.environ[ "_CONTAINER_LOCAL_CONFIGENDPOINTKEY" ]

    if endpoint_key.endswith( "_LOCAL_CONFIGENDPOINTKEY_" ) : return

    #set_key_alt( "endpoint/key" , endpoint_key ) 
    set_key( "endpoint/key" , endpoint_key ) 




def handle_key_public( ) :

    if( get_key( "endpoint/url"  ) != False ) : return

    set_key_alt( "endpoint/url" , "https://sapiomnibus-public.sparc.space" )

def handle_sslverify_fornumericip( ) :

    endpoint_url = get_key( "endpoint/url" )

    if( not endpoint_url ) :
        return

    #s_log.write(endpoint_url)
    purl = s_util.url_parse( endpoint_url )
    #s_log.write(purl.scheme)
    #s_log.write(purl.hostname)
    #s_log.write(purl.port)

    if( not purl.hostname ) :
        return

    if( s_util.is_ip( purl.hostname ) ):
        set_key_alt( "endpoint/sslverify" , "no" )
        return

    ########################################################

    host = get_key( "endpoint/host" )
    #s_log.write(host)
    if( not host ) : return

    if host.endswith(".test"):
        set_key_alt( "endpoint/sslverify" , "no" )


def unpack_key( ) :

    # TOKEN|IP:PORT|HOST
    # DEF|DEF|DEF

    endpoint_key = get_key( "endpoint/key" )

    #s_log.write(endpoint_key)

    if( not endpoint_key ) :
        return

    ########################################################

    key_parts = endpoint_key.split( "|" )
    key_parts_total = len( key_parts )
    # s_log.write( key_parts_total )

    ########################################################

    if( key_parts_total != 3 ) :
        s_log.write( "key_parts_total != 3 " )
        return

    ########################################################

    #if( ( key_parts[ 0 ] != "*" ) and ( len( key_parts[ 0 ] ) == 67 ) ) :
    #    #set_key_alt( "endpoint/token" , key_parts[ 0 ] )
    #   set_key( "endpoint/token" , key_parts[ 0 ] )
    set_key( "endpoint/token" , key_parts[ 0 ] )

    ########################################################

    if( ( key_parts[ 1 ] != "*" ) ) :
        url = key_parts[ 1 ]
        if( url[ 0:4 ] != "http" ) : url = "https://" + url
        #set_key_alt( "endpoint/url" , url )
        set_key( "endpoint/url" , url )

    ########################################################

    if( ( key_parts[ 2 ] != "*" ) ) :
        #set_key_alt( "endpoint/host" , key_parts[ 2 ] )
        set_key( "endpoint/host" , key_parts[ 2 ] )

    ########################################################

    # FIXME TODO do not use ALT config ?

    #s_log.write(url)
    #purl = s_util.url_parse(url)
    #s_log.write(purl.scheme)
    #s_log.write(purl.hostname)
    #s_log.write(purl.port)


    return

def isready( ) :
    return( ready )


def get_config( ) :
    # FIXME TODO merge alt config... otherwise you dont have full picture
    # FIXME TODO have log that outputs both config and alt!
    return config
def get_config_alt( ) :
    # FIXME TODO merge alt config... otherwise you dont have full picture
    # FIXME TODO have log that outputs both config and alt!
    return config_alt


def set_key( config_key , config_val ) :
    global config
    #s_log.write( "CONFIG SET_KEY " + config_key + " = " + str( config_val ) )
    config[ config_key ] = config_val
    return True

def set_key_alt( config_key , config_val ) :
    global config_alt
    #s_log.write( "CONFIG SET_KEY " + config_key + " = " + str( config_val ) )
    config_alt[ config_key ] = config_val
    return True

def del_key_alt( kn ) :
    global config_alt
    #s_log.write_msg("GET KEY "+config_key)
    if( kn in config_alt ) :
        #s_log.write_msg("GET KEY FOUND")
        config_alt.pop( kn )
        return True
            
    #s_log.write_msg("GET KEY NULL")
    return False

def key_is_yes( kn ) :
    v = get_key( kn )
    if(v=="yes"): return(True)
    return(False)

def key_is_no( kn ) :
    v = get_key( kn )
    if( v == "no" ) : return( True )
    return( False )

def del_key( kn ) :
    #s_log.write_msg("GET KEY "+config_key)
    if( kn in config ) :
        #s_log.write_msg("GET KEY FOUND")
        config.pop( kn )
        return True
            
    #s_log.write_msg("GET KEY NULL")
    return False

################################################################

def init_fromfile( config_path , config_key = "sapiadapter" ) :

    global config

    #s_log.write( os.getcwd( ) + "," + config_path )

    try :

        with open( config_path ) as f :
            config_all = json.load( f )
    
    except IOError :

        s_log.write( "config init_fromfile IOError " + config_path )
        return False

    ####################################################################

    if config_key in config_all :
        config.update( config_all[ config_key ] )
        #config["config/init_fromfile" ] = "yes"
        config[ "/config/init/path" ] = config_path
        config[ "/config/init/path_time" ] = os.path.getmtime( config_path )
    else :
        s_log.write( "ERROR config_key " + config_key )
        return False

    ####################################################################

    # s_log.write( "LOADED " + config_path )
    # s_log.write( config )

    return True

def load_from_file( cp ) :
    if not os.path.isabs(cp):
        s_log.write( "load_from_file file path not absolute" )
        return( False )
    if not os.path.isfile( cp ) :
        s_log.write( "load_from_file file not found" )
        return( False )

    if not init_fromfile( cp ) :
        s_log.write( "load_from_file init_fromfile false" )
        return( False )

    unpack_key( )   
    config[ "/config/init/from" ] = "manual_file"
    s_log.write( "CONFIG MANUAL" ) 
    s_log.write( config ) 
    return( True )


################################################################

def init( config_user = None ) :

    global config

    config = { }

    # Use "/..." for internal config keys...

    t1 = time.time( )
    config[ "/config/init/time" ] = t1
    config[ "/config/init/time_lap" ] = t1
    config[ "/config/version" ] = get_version( )
    config[ "/config/cwd" ] = os.getcwd( )
    #config[ "/config/scriptdir" ] = os.path.dirname( os.path.realpath( __file__ ) )
    config[ "/config/session" ] = s_util.uhash( )


    config[ "/config/parentpath" ] = s_util.parent_path()

    #s_log.write( config )

    if( config_user ) :
        config.update( config_user )
        config[ "/config/init/from" ] = "config_user"
        preprocess()
        return( True ) 

    ################################################################

    # First check env variable SAPIADAPTER
    if( "SAPIADAPTER " in os.environ ) :
        #s_log.write( "Found env var SAPIADAPTER_CONFIGURATION" )
        if( init_fromfile( os.environ[ "SAPIADAPTER_CONFIGURATION" ] ) ) :
            s_log.write( "Loaded SAPIADAPTER_CONFIGURATION " + os.environ[ "SAPIADAPTER_CONFIGURATION" ] )
            config[ "/config/init/from" ] = "environ_file"
            preprocess()
            return( True )
        else :
            return( False )

    #s_log.write( "Not found env var SAPIADAPTER_CONFIGURATION" )

    ################################################################

    config_default_filename = "local_sapiadapter_config.json"

    # Lets check current directory for config file

    if os.path.isfile( config_default_filename ) :
        if( init_fromfile( config_default_filename ) ) :
            s_log.write( "Loaded " + config_default_filename )
            config[ "/config/init/from" ] = "cwd_file"
            preprocess()
            return( True )
        return( False )

    #s_log.write( "Not found " + os.getcwd( ) + "/" + config_default_filename )

    ################################################################

    # Lets check tests directory for config file
    testpath = "tests/data/"
    if os.path.isfile( testpath + config_default_filename ) :
        if( init_fromfile( testpath + config_default_filename ) ) :
            s_log.write( "Loaded " + testpath + config_default_filename )
            config[ "/config/init/from" ] = "testsdata_file"
            preprocess()
            return( True )
        return( False )

    ################################################################

    #try:
    #    config[ "/config/maindir" ] = os.path.dirname( sys.modules[ "__main__" ].__file__ )
    #except:
    #    s_log.write("maindir main/file EXCEPTION")

    # Lets check 'main' directory for config file
    #testpath = config[ "/config/maindir" ] + "/" + config_default_filename
    #if os.path.isfile( testpath ) :
    #    if( init_fromfile( testpath ) ) :
    #        s_log.write( "Loaded " + testpath )
    #        config[ "/config/init/from" ] = "maindir_file"
    #        return( True )
    #    return( False )

    #s_log.write( "Not found " + os.getcwd( ) + "/" + testpath + config_default_filename )


    s_log.write( "No loading from config file" )

    preprocess()

    return( True )
