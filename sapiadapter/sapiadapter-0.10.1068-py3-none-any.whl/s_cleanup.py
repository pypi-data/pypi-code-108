
#####################################################################
#
# s_cleanup.py
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

import atexit

#####################################################################

from . import s_log , s_db

#####################################################################

def cleanup( ) :
    #pass
    s_db.fdelete( )
    #s_log.write( "cleanup" )

#####################################################################

atexit.register( cleanup )
    