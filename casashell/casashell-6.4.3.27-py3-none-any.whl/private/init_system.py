###
### add configuration files for casatools and casatasks
###
import sys
from casashell.private import config
from casashell import argv
sys.path.append(config.internal_configpath)

def __static__(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

###
### This is not so great. The configuration is set up outside of our ipython instance.
### This means that we must traverse back and pull in the configuration to make it
### available (not only for the CASA users and scripts, but also to configure
### casatools and casatasks...
###
def __incfg__( ):
    import config as newcfg
    import casatoolrc as newtool
    import casataskrc as newtask
    import inspect
    origcfg = None
    frame = inspect.currentframe( )
    while frame is not None:
        if 'casa_config_master' in frame.f_locals:
            origcfg = frame.f_locals['casa_config_master']
            break
        frame = frame.f_back

    if origcfg is None:
        import os
        print("configuration initalization failed")
        os._exit(1)
    else:
        for cfg in dir(origcfg):
            if cfg == 'datapath' and origcfg.datapath is not None:
                newtool.datapath = origcfg.datapath
                newcfg.datapath = origcfg.datapath
            elif cfg == 'logfile' and origcfg.logfile is not None:
                newtask.logfile = origcfg.logfile
                newcfg.logfile = origcfg.logfile
            elif cfg == 'rcdir' and origcfg.rcdir is not None:
                newtask.rcdir = origcfg.rcdir
                newcfg.rcdir = origcfg.rcdir
            elif cfg == 'nogui':
                newtool.nogui = origcfg.nogui
                newcfg.nogui = origcfg.nogui
            elif cfg == 'agg':
                newtool.agg = origcfg.agg
                newcfg.agg = origcfg.agg
            elif cfg == 'pipeline':
                newtool.pipeline = origcfg.pipeline
                newcfg.pipeline = origcfg.pipeline
            elif not cfg.startswith('_'):
                setattr(newcfg,cfg,getattr(origcfg,cfg))

__incfg__( )

###
### ensure that the CASA modules are available within the shell
###
import casatools
import casatasks

###
### import legacy tools if available...
###
try:
    import casalith
except:
    pass

try:
    from casalith import browsetable
except:
    pass

try:
    from casalith import msuvbin
except:
    pass

try:
    from almatasks.gotasks.wvrgcal import wvrgcal
except:
    pass
try:
    from casaviewer.gotasks.imview import imview
    @__static__('state',{'warned': False})
    def viewer( *args, **kwargs ):
        if not viewer.state['warned']:
            from casatasks import casalog
            casalog.origin('viewer')
            viewer.state['warned'] = True
            casalog.post("the viewer task is deprecated, please use imview instead", "WARN") 
        return imview( *args, **kwargs )
except:
    try:
        from casaviewer import imview
        @__static__('state',{'warned': False})
        def viewer( *args, **kwargs ):
            if not viewer.state['warned']:
                from casatasks import casalog
                casalog.origin('viewer')
                viewer.state['warned'] = True
                casalog.post("the viewer task is deprecated, please use imview instead", "WARN") 
            return imview( *args, **kwargs )
    except:
        pass
try:
    from casaviewer.gotasks.msview import msview
except:
    try:
        from casaviewer import msview
    except:
        pass
try:
    from casaplotms.gotasks.plotms import plotms
except:
    try:
        from casaplotms import plotms
    except:
        pass

# When in monolithic CASA, the servers must start their serve() loop now
# (CAS-12799), after all the tasks, etc that might be used by the pipeline
# and/or advanded users of parallel mode that push imports to servers.
try:
    import importlib
    _clith_spec = importlib.util.find_spec("casalith")
    if _clith_spec is not None:
        import casampi.private.start_mpi
except ImportError:
    pass

###
### start logger if the executable can be found and the log file
### is writable... (this will need to be adjusted for MacOS)
###

### Try config.flags.nologger first, else look for it in argv
dologger = True
try:
    dologger = not config.flags.nologger
except:
    dologger = '--nologger' not in argv

if dologger:
    from shutil import which
    logger = which('casalogger')
    if logger is not None:
        import os
        log = casatools.logsink( ).logfile( )
        if os.access( log, os.W_OK ):
            import subprocess 
            import atexit
            try:
                p = subprocess.Popen([logger,log])
                def stop_logger( ):
                    p.kill( )
                atexit.register(stop_logger)
            except:
                pass

###
### execfile(...) is required by treaties and obligations (CAS-12222), but
### only in CASAshell...
###
def execfile(filename,globals=globals( ),locals=None):
    from runpy import run_path
    newglob = run_path( filename, init_globals=globals )
    for i in newglob:
        globals[i] = newglob[i]


###
### checkgeodetic() - verify the contents of the most important Measures tables
###
def checkgeodetic():
    """
    Verify the contents of the most important Measures tables
    """
    import os
    from casatools import ctsys
    from casatools import table as tbtool
    from casatools import quanta as qatool
    from casatasks import casalog
    rval = True
    geodeticdir = ctsys.rundata()+'/geodetic' #os.path.dirname(ctsys.resolve('geodetic/IERSpredict'))
    if not os.path.isdir(geodeticdir):
        casalog.post('Data repository directory not found. Cannot check Measures tables. Retrieved path was \"'+geodeticdir+'\"', 'WARN')
        rval = False
    else:
        casalog.post('\n', 'INFO')
        casalog.post('Checking Measures tables in data repository sub-directory '+geodeticdir, 'INFO')
        mytb = tbtool()
        mytables=['IERSeop2000', 'IERSeop97', 'IERSpredict', 'TAI_UTC']
        for mytable in mytables:
            if not os.path.isdir(geodeticdir+'/'+mytable):
                casalog.post('Measures table '+mytable+' does not exist. Expected at '+geodeticdir+'/'+mytable, 'WARN')
                rval = False
            else:
                mytb.open(geodeticdir+'/'+mytable)
                vsdate = mytb.getkeyword('VS_DATE')
                mjd = mytb.getcol('MJD')
                if len(mjd)>0:
                    myqa = qatool()
                    mydate = myqa.time({'value': mjd[-1], 'unit': 'd'}, form='ymd')[0]
                    casalog.post('  '+mytable+' (version date, last date in table (UTC)): '+vsdate+', '+mydate, 'INFO')
                else:
                    casalog.post(mytable+' contains no entries.', 'WARN')
                    rval = False
                mytb.close()
    return rval


###
### evaluate scriptpropogating errors out of ipython
###
def __evprop__(args):
    import os
    import sys
    from runpy import run_path
    exit_status = None
    if len(args) > 0:
        try:
            if os.path.isfile(args[0]):
                import sys
                exec_globals = globals( )
                exec_globals['sys'].argv = args
                run_path( args[0], init_globals=exec_globals, run_name='__main__' )
            else:
                for stmt in args:
                    exec(stmt)
        except SystemExit as err:
            exit_status = { 'code': err.code, 'desc': 'system exit called' }
        except:
            import traceback
            traceback.print_exc(file=sys.stderr)
            exit_status = { 'code': 1, 'desc': 'exception: %s' % sys.exc_info()[0] }
    else:
        exit_status = { 'code': 1, 'desc': 'no file or statement' }

    if exit_status is not None:
        import inspect
        frame = inspect.currentframe( )
        while frame is not None:
            if 'casa_eval_status' in frame.f_locals and \
               type(frame.f_locals['casa_eval_status']) is dict:
                status = frame.f_locals['casa_eval_status']
                for k in exit_status:
                    status[k] = exit_status[k]
                break
            frame = frame.f_back

###
### set the CASA prompt
###
from IPython.terminal.prompts import Prompts, Token

class _Prompt(Prompts):
     def in_prompt_tokens(self, cli=None):
         return [(Token.Prompt, 'CASA <'),
                 (Token.PromptNum, str(self.shell.execution_count)),
                 (Token.Prompt, '>: ')]

_ip = get_ipython()
try:
    ## generally thought to make tab completion faster...
    _ip.Completer.use_jedi = False
except: pass

_ip.prompts = _Prompt(_ip)

del __static__
