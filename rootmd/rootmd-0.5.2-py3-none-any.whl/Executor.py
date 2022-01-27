
# from asyncio import subprocess
import select
from subprocess import Popen, PIPE, run

import re
import rich
# from . import log

import logging
from rich.logging import RichHandler
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")



class Executor:
    def __init__(self, cmd) -> None:
        log.debug("Executor")
        self.cmd = cmd
        self.p = Popen(cmd, stdin=PIPE, stdout=PIPE, 
        stderr=PIPE, 
        universal_newlines=True, bufsize=1)
        # capture any of that initial stuff ROOT prints out
        self.run_cmd( "" )


    def read_available(self, s, time_limit=0):
        return ""


    def run_cmd( self, code ):
        return ("", "", "")




class RootExecutor(Executor):
    def __init__(self, **kwargs) -> None:
        log.debug("RootExecutor")
        super().__init__( [ 'root', '-b', '-l' ])

    def read_available(self, s, time_limit=0):
        pass
        output = ""
        while True:
            poll_result = select.select([s], [], [], time_limit)[0]
            if len(poll_result) > 0 :
                l = s.readline()
                if ( "ROOTEOF" in l ):
                    return output
                output += l
            elif time_limit != None:
                break
        return output
    
    def run_cmd( self, code ):
        # return ("", "", "")
        code_lines = [ l + '\n\r' for l in code.splitlines()]
        code_lines.append( 'cout << "ROOTEOF" << endl;\r' ) # needed to signal end of read, else deadlock
        code_lines.append( 'cerr << "ROOTEOF" << endl;\r' ) # needed to signal end of read, else deadlock
        self.p.stdin.writelines( code_lines )
        output = self.read_available( self.p.stdout, None)
        err = self.read_available( self.p.stderr, None)
        log.debug( ">\n%s" % output )
        log.debug( ">\n%s" % err )

        # get image names from output to cerr
        imgs = []
        for m in re.findall( "file *(.*) *has", err ):
            imgs.append(m)
        return (output, err, imgs)


class GnuPlotExecutor:
    def __init__(self) -> None:
        pass

    def run( self, code ):
        cmd = ['gnuplot' ]
        incode = code.encode('utf-8')
        result = run( cmd, stdout=PIPE, input=incode )
        rich.inspect( result )
        return result.stdout.decode('utf-8')
    

    def find_output( self, code ) :
        outs = []
        # find the terminal output in the code
        ms = re.finditer( 'set *output *(\'|")(.*)(\'|")', code )
        for m in ms :
            if m:
                # rich.inspect(m)
                # log.info( m.groups()[1] )
                outs.append( m.groups()[1] )
        return outs

class RnuPlotExecutor:
    def __init__(self) -> None:
        pass

    def run( self, code ):
        incode = code.encode('utf-8')
        with open( "tmp.rnuplot", "w" ) as fw :
            fw.writelines( code )

        cmd = ['rnuplot', 'tmp.rnuplot' ]
        result = run( cmd, stdout=PIPE )
        rich.inspect( result )
        return result.stdout.decode('utf-8')
    

    def find_output( self, code ) :
        outs = []
        # find the terminal output in the code
        ms = re.finditer( 'set *output *(\'|")(.*)(\'|")', code )
        for m in ms :
            if m:
                # rich.inspect(m)
                # log.info( m.groups()[1] )
                outs.append( m.groups()[1] )
        return outs