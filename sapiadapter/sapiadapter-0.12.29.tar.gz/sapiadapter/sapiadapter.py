
#####################################################################
#
# sapiadapter.py
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

from . import s_log , s_config , s_net , s_util , s_db , s_cleanup

#####################################################################

#s_log.write( "    ####    ####    ####    ####\n" )

#####################################################################

s_config.setup( )
s_db.setup( )

#s_log.write( s_config.get_key( "/config/version" ) ) 

#####################################################################

def isready( ) :

    if( not s_util.ready( ) ) :
        s_log.write( "ERROR False ready" )
        return( False )

    #s_log.write( "OK" )
    return( True )

#####################################################################

def config_load_from_file( cp ) :
    return( s_config.load_from_file( cp ) )

def prexit( msg ) :
    s_util.printexit( msg )

def defdata( ) :
    return( s_db.meta_read( "_data" ) )

def defmeta( ) :
    return( s_db.meta_read( "_meta" ) )

def flush( ) :
    return( s_db.flush( ) )

def uptime( ) :
    return( s_util.uptime( ) )
def uptime_lap( ) :
    return( s_util.uptime_lap( ) )
def log_lap( ) :
    s_log.write( s_util.uptime_lap( ) )

def heartbeat( t = 60 ) :
    return( s_util.heartbeat( t ) )

def server( runner , debug_errorprexit = False ) :

    s_log.write( "SERVER START" )

    while True :

        s_log.write( "SERVER LOOP" )

        heartbeat( )

        #####################################################

        try :
            flag_jobget = s_net.job_get( )
        except Exception as e :
            s_log.write( "Exception job_get" )
            s_util.printexception( )
            # FIXME TODO add flags to server
            if debug_errorprexit : prexit( "EXCEPTION job_get" )
            print( "Exception job_get" )
            continue
            #sys.exit( 99 )

        #####################################################
        
        if flag_jobget == False :

            #s_config.get_key( "endpoint/url" ) 
            s_log.write( "ERROR False job_get" )
            if debug_errorprexit : prexit( "ERROR False job_get" )
            print( "ERROR False job_get" )
            continue

        if flag_jobget == None :
            continue

        #####################################################

        params = s_db.meta_read( "_params" )

        if( not params ) :
            s_log.write( "TESTS PING NO PARAMS" )
            #print(defmeta["_ping_5800b137d"])
            #s_db.setup( )
            defdata = [ "_ping_5800b137d" ] 
            defmeta = {
                "_ping_5800b137d" : "?" 
            }
            s_db.meta_create( "_data" , defdata )
            s_db.meta_create( "_meta" , defmeta)
            #s_db.files_defdata_set( defdata )
            #s_db.files_defmeta_set( defmeta)
            s_db.meta_create( "_runner_exitflag" , True )
            s_net.job_set( )
            s_log.write( "OK PINGPONG" )
            continue

        if( "_ping_5800b137d" in params ) :
            s_log.write( "TESTS PING" )
            #print(defmeta["_ping_5800b137d"])
            t1 = params[ "_ping_5800b137d" ]
            #s_db.setup( )
            defdata = [ "_ping_5800b137d" ] 
            defmeta = {
                "_ping_5800b137d" : "." + t1
            }
            s_db.meta_create( "_data" , defdata )
            s_db.meta_create( "_meta" , defmeta)
            #s_db.files_defdata_set( defdata )
            #s_db.files_defmeta_set( defmeta)
            s_db.meta_create( "_runner_exitflag" , True )
            s_net.job_set( )
            s_log.write( "OK PINGPONG" )
            continue

        #####################################################

        #if( not s_util.proc_setup( ) ) :
        #    continue

        #####################################################

        #s_util.proc_run( )

        #####################################################

        #s_util.proc_storage( )
        #s_util.proc_teardown( )

        #####################################################

        #config = { 
        #    "_env" : s_util.container_appenvstatic_get( )
        #}
        runner_output = runner( )
        s_db.meta_create( "_runner_exitflag" , runner_output )

        s_net.job_set( )

        #####################################################

        s_log.write( "OK" )

    s_log.write( "SERVER END" )



#####################################################################

# DATA
# TIMEOUT
def run( params = { } , wait_timeout = 60 ) :

    #if( not ready( ) ) :
    #    s_log.write( "NOT READY" )
    #    return( False )

    if( not isinstance( params , ( dict ) ) ) :
        s_log.write( "false params dict" )
        return( False )

    #####################################################################

    #s_db.flush( ) 

    #####################################################################

    s_db.meta_create( "_params" , params )

    #####################################################################

    if not s_net.job_request( params ) :
        s_log.write( "false job_request" )
        return( False )

    #####################################################################

    jid = s_config.get_key( "jid" )

    if( jid == False ) :
        s_log.write( "false job_request jid" )
        return( False )

    #####################################################################

    #s_log.write( s_db.meta_read( "_test_run_withresponse" ))
    jr = s_net.job_responsewait( jid , wait_timeout )
    #s_log.write( s_db.meta_read( "_test_run_withresponse" ))

    if( jr == False ) :
        s_log.write( "false job_wait" )
        return( False )

    if( jr == None ) :
        s_log.write( "none job_wait" )
        return( None )

    #####################################################################

    if( s_db.stdio_has_stderr( ) ) :
        s_log.write( "ERROR stdio_has_stderr " + s_db.stdio_get_stderr( ) )
        return( None )

    #####################################################################

    if( s_db.meta_read( "_runner_exitflag" ) == False ) :
        return( False )

    dd = defdata( )
    if( dd == False ) : return( True )
    return( dd )
