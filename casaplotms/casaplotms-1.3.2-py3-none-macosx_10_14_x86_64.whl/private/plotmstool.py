##########################################################################
#
# Copyright (C) 2019
# Associated Universities, Inc. Washington DC, USA.
#
# This script is free software; you can redistribute it and/or modify it
# under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
# License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning AIPS++ should be adressed as follows:
#        Internet email: aips2-request@nrao.edu.
#        Postal address: AIPS++ Project Office
#                        National Radio Astronomy Observatory
#                        520 Edgemont Road
#                        Charlottesville, VA 22903-2475 USA
###########################################################################
import os as __os
import sys as __sys
import pwd as __pwd
import time as __time
from numbers import Real as _real_t
import traceback
from casatasks import casalog

###
### TODO:   (1) perhaps add __main__ which execs casaplotms app
###             https://stackoverflow.com/a/55346918
###

###
### Load the necessary gRPC libraries and bindings.
###
### The generated wrappers assume that all of the wrappers can be
### loaded using the standard sys.path so here we add the path to
### the wrappers, load all of the needed wrappers, and then remove
### the private path (cwd) from sys.path
###
__sys.path.insert(0, __os.path.dirname(__os.path.abspath(__file__)))
import grpc as __grpc
from . import shutdown_pb2_grpc as __sd
from . import ping_pb2_grpc as __ping
from google.protobuf import empty_pb2 as __empty_p
from . import plotms_pb2 as __plotms_p
from . import plotms_pb2_grpc as __plotms_rpc
__sys.path.pop(0)

__proc = None
__stub = None
__uri = None
__registered = False
__try_check_health = True

debug = False
###
### When casaplotms is started (via __launch) without casatools, this function
### is called to shutdown the casaplotms app when the user exits python.
###
def __shutdown_sans_casatools( ):
    global __uri
    casalog.post('Running shutdown_sans_casatools, grpc shutdownStub.now()...', 'DEBUG')
    if __uri is not None:
        channel = __grpc.insecure_channel(__uri)
        shutdown = __sd.ShutdownStub(channel)
        shutdown.now(__empty_p.Empty( ))
        __uri = None

def __hack_terminate_proc(proc, terminate=True):
    """
    Makes sure a (sub)process terminates. CAS-10031.
    At the moment it sends a relatively gentle SIGTERM (if terminate=True) and polls every
    sec up to 5 sec.
    With terminate=True it normally terminates within 1s, and the exit code is -15.
    Without it it might take 4s, and the exit code is 0.

    :param proc: a (Popen) process object
    :param terminate: whether to send a SIGTERM or be more patient
    """
    if terminate:
        casalog.post('Terminating casaplotms, PID: {}'.format(proc.pid), 'INFO')
        proc.terminate()

    max_cnt_secs = 5
    cnt = 0
    while proc.poll() is None and cnt < max_cnt_secs:
        casalog.post('Waiting for casaplotms to terminate. Poll return code: {}, PID: {}'.
                     format(proc.returncode, proc.pid), 'INFO')
        __time.sleep(1)
        cnt +=1

    if cnt >= max_cnt_secs:
        casalog.post('Over {} seconds past after trying to terminate casaplotms (PID {}). '
                     'Giving up. The CASA shutdown might not be clean.'.format(max_cnt_secs,
                                                                               proc.pid),
                     'WARN')
    casalog.post('Finished shutting down casaplotms. Poll return code: {}, PID: {}'.
                 format(proc.returncode, proc.pid), 'INFO')

###
### A named-pipe is used for communication when casaplotms is started
### without casatools. The --server=... flag to the casaplotms app
### accepts wither a named pipe (path) or a gRPC URI. The URI for
### the casaplotms app is passed back through the named pipe.
###
def __fifo_name(index):
    count = 0
    path = "/tmp/._casaplotms_%s_%s_%s_" % (__pwd.getpwuid(__os.getuid()).pw_name, __os.getpid( ), count)
    while __os.path.exists(path):
        count = count + 1
        path = "/tmp/._casaplotms_%s_%s_%s_" % (__pwd.getpwuid(__os.getuid()).pw_name, __os.getpid( ), count)
    return path

###
### Create a named pipe...
###
def __mkfifo( ):
    path =  __fifo_name(0)
    __os.mkfifo(path)
    return path

###
### Launch the casaplotms app in either the casatools context (gRPC URI)
### or the stand-alone context (named pipe).
###
def __launch( uri=None ):
    from subprocess import Popen, STDOUT
    global __proc
    global __uri
    np_path = None
    data_path = [ ]
    try:
        from casatools import ctsys as ct
        data_path = [ "--datapath=%s" % ct.rundata( ) ]
    except: pass
    if __uri is None:
        if uri is not None:
            __uri = uri
        else:
            app_path = __os.path.join( __os.path.abspath( __os.path.join(__os.path.dirname(__file__),"..") ), '__bin__/casaplotms.app/Contents/MacOS/casaplotms')
            try:
                ### remove 'xxx' after non-casatools setup has been debugged
                from casatoolsxxx import ctsys
                with open(__os.devnull, 'r+b', 0) as DEVNULL:
                    __proc = Popen( [ app_path, '--nopopups', '--logfilename=%s' % casalog.logfile( ),
                                    '--server=%s' % ctsys.registry( )['uri'] ] + data_path,
#                                   stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT,
#                                   stdin=DEVNULL, stdout=STDOUT, stderr=STDOUT,
                                    close_fds=True,
                                    env={k:v for k,v in __os.environ.copy().items() if 'MPI' not in k} )
                __time.sleep(1) # give it a second to launch
                count = 0
                while __uri is None and count < 50: # search for registered plotms
                    for k,v in ctsys.services( ).items( ):
                        if 'id' in v:
                            id = v['id'].split(':')[0]
                            if id == 'casaplotms':
                                __uri = v['uri']
                                break
                    count = count + 1
                    __time.sleep(1)
                if __uri is None:
                    print("could not sync with casaplotms...")
            except ModuleNotFoundError:
                try:
                    np_path = __mkfifo( )
                    with open(__os.devnull, 'r+b', 0) as DEVNULL:
#                       __proc = Popen( [ app_path, '--server=%s' % np_path ],
#                                       stdin=DEVNULL, stdout=STDOUT, stderr=STDOUT,
#                                       close_fds=True )
#                       __proc = Popen( [ '/usr/bin/valgrind', '/home/hypnos/dschieb/casa/casaplotms/build/bin.3.10.0-957.21.2.el7.x86_64/casaplotms.app/usr/bin/casaplotms', '--nopopups', '--server=%s' % np_path ] )
#                       __proc = Popen( [ '/home/hypnos/dschieb/casa/casaplotms/build/bin.3.10.0-957.21.2.el7.x86_64/casaplotms.app/usr/bin/casaplotms', '--nopopups', '--server=%s' % np_path ] )

                        __proc = Popen( [ app_path, '--nopopups', '--logfilename=%s' % casalog.logfile( ),
                                          '--server=%s' % np_path ] + data_path,
                                        env={k:v for k,v in __os.environ.copy().items() if 'MPI' not in k} )

                    with open( np_path, 'r' ) as input:
                        __uri = input.readline( ).rstrip( )
                    casalog.post("casaplotms started: %s" % __uri)
                    __os.remove(np_path)
                    global __registered
                except Exception as exc:
                    casalog.post("error: casaplotms launch failed with an exception. "
                                 "Details: {}".format(exc), 'SEVERE')
                    __uri = None
                    __os.remove(np_path)

            if not __registered and __proc is not None and __uri is not None:
                import atexit
                # First, grpc shutdown, then make sure casaplotms process terminates before
                # it's too late (X / xvfb might go very quickly after CASA exits).
                atexit.register(__hack_terminate_proc, __proc)
                atexit.register(__shutdown_sans_casatools)
                __registered = True

    return __uri

def __stub_check( _stub, uri ):
    global __stub, __try_check_health, __proc, __uri
    if _stub is None:
        raise RuntimeError("invalid plotms stub")
    if uri is None:
        ### check could be improved
        raise RuntimeError("invalid plotms uri")
    if __try_check_health:
        try:
            channel = __grpc.insecure_channel(uri)
            ping = __ping.PingStub(channel)
            if debug: print("pinging plotms...")
            ping.now(__empty_p.Empty( ),timeout=5)
            if debug: print("plotms responded to ping...")
            return _stub
        except:
            from casatasks import casalog
            from casatools import ctsys
            print("plotms did not responded to ping... restarting...")
            __proc.kill( )
            __proc = None
            __stub = None
            ### casaplotms does not register with the registry so it is
            ### not necessary to remove the service with:
            ###
            ### ctsys.remove_service( uri ):
            ###
            casalog.post("plotms failure detected [%s] restarting" % uri)
            __uri = None
            return stub( )
    else:
        return _stub

        
###
### Get the casaplotms app proxy; if the casaplotms app has not been
### launched, then the first time stub is called it will launch the
### casaplotms app and create the stub either by reading the app's
### URI through a named pipe or retrieving it from the casatools
### registry.
###
def stub( uri_param=None ):
    global __stub, __uri
    uri = None
    if __stub is None:
        uri = __launch( uri_param )
        if uri is None:
            print("error: casaplotms launch failed...")
        else:
            channel = __grpc.insecure_channel(uri)
            __stub = __plotms_rpc.appStub(channel)
    return __stub_check( __stub, uri if uri is not None else __uri )

def getPlotMSPid( ):
    if (debug): print("<debug>          pm.getPlotMSPid( )")
    return stub( ).getPlotMSPid(__empty_p.Empty( )).id

def getNumPlots( ):
    if (debug): print("<debug>          pm.getNumPlots( )")
    return stub( ).getNumPlots(__empty_p.Empty( )).nplots

def setShowGui(show):
    if (debug): print("<debug>          pm.setShowGui(%s)" % repr(show))
    if type(show) != bool:
        raise Exception("show parameter should be a boolean")
    sg = __plotms_p.Toggle( )
    sg.state = show
    stub( ).setShowGui(sg)

def setGridSize( rowCount=1, colCount=1 ):
    if (debug): print("<debug>          pm.setGridSize(%s,%s)" % (repr(rowCount),repr(colCount)))
    if type(rowCount) != int or type(colCount) != int:
        raise Exception("setGridSize only accepts two integer parameters")
    sgs = __plotms_p.GridSize( )
    sgs.rows = rowCount
    sgs.cols = colCount
    stub( ).setGridSize(sgs)

def isDrawing( ):
    if (debug): print("<debug>          pm.isDrawing( )")
    return stub( ).isDrawing(__empty_p.Empty( )).state

def clearPlots( ):
    if (debug): print("<debug>          pm.clearPlots( )")
    stub( ).clearPlots(__empty_p.Empty( ))

def setPlotMSFilename( msFilename, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSFilename(%s,%s,%s)" % (repr(msFilename),repr(updateImmediately),repr(plotIndex)))
    if type(msFilename) != str:
        raise Exception("msFilename argument must be a path/string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    svis = __plotms_p.SetVis( )
    svis.name = msFilename
    svis.update = updateImmediately
    svis.index = plotIndex
    stub( ).setPlotMSFilename(svis)

def setPlotAxes( xAxis="", yAxis="", xDataColumn="", yDataColumn="", xFrame="", yFrame="",
                 xInterp="", yInterp="", yAxisLocation="", updateImmediately=True,
                 plotIndex=0, dataIndex=0 ):
    if (debug): print("<debug>          pm.setPlotAxes(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(xAxis), repr(yAxis), repr(xDataColumn), repr(yDataColumn), repr(xFrame), repr(yFrame), repr(xInterp), repr(yInterp), repr(yAxisLocation), repr(updateImmediately), repr(plotIndex), repr(dataIndex)))
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    if type(dataIndex) != int:
        raise Exception("dataIndex must be an integer")
    if type(xAxis) != str:
        raise Exception("xAxis must be a string")
    if type(yAxis) != str:
        raise Exception("yAxis must be a string")
    if type(xDataColumn) != str:
        raise Exception("xDataColumn must be a string")
    if type(yDataColumn) != str:
        raise Exception("yDataColumn must be a string")
    if type(xFrame) != str:
        raise Exception("xFrame must be a string")
    if type(yFrame) != str:
        raise Exception("yFrame must be a string")
    if type(xInterp) != str:
        raise Exception("xInterp must be a string")
    if type(yInterp) != str:
        raise Exception("yInterp must be a string")
    if type(yAxisLocation) != str:
        raise Exception("yAxisLocation must be a string")

    if xDataColumn == "residual" or xDataColumn == "corrected-model":
        xDataColumn = "corrected-model_vector"
    if yDataColumn == "residual" or yDataColumn == "corrected-model":
        yDataColumn = "corrected-model_vector"
    if xDataColumn == "corrected/model":
        xDataColumn = "corrected/model_vector"
    if yDataColumn == "corrected/model":
        yDataColumn = "corrected/model_vector"

    if xDataColumn == "data-model":
        xDataColumn = "data-model_vector"
    if yDataColumn == "data-model":
        yDataColumn = "data-model_vector"
    if xDataColumn == "data/model":
        xDataColumn = "data/model_vector"
    if yDataColumn == "data/model":
        yDataColumn = "data/model_vector"

    setpa = __plotms_p.SetAxes( )
    setpa.index = plotIndex
    setpa.dataindex = dataIndex
    setpa.update = updateImmediately
    setpa.x = xAxis
    setpa.y = yAxis
    setpa.xframe = xFrame
    setpa.yframe = yFrame
    setpa.xdata = xDataColumn
    setpa.ydata = yDataColumn
    setpa.xinterp = xInterp
    setpa.yinterp = yInterp
    setpa.yaxisloc = yAxisLocation
    stub( ).setPlotAxes(setpa)

def setShowAtm( showatm=False, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setShowAtm(%s,%s,%s)" % (repr(showatm),repr(updateImmediately),repr(plotIndex)))
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    if type(showatm) != bool:
        raise Exception("showatm must be a boolean")
    setsa = __plotms_p.SetToggle( )
    setsa.state = showatm
    setsa.update = updateImmediately
    setsa.index = plotIndex
    stub( ).setShowAtm(setsa)

def setShowTsky( showtsky=False, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setShowTsky(%s,%s,%s)" % (repr(showtsky),repr(updateImmediately),repr(plotIndex)))
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    if type(showtsky) != bool:
        raise Exception("showtsky must be an boolean")
    setst = __plotms_p.SetToggle( )
    setst.state = showtsky
    setst.update = updateImmediately
    setst.index = plotIndex
    stub( ).setShowTsky(setst)

def setShowImage( showimage=False, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setShowImage(%s,%s,%s)" % (repr(showimage),repr(updateImmediately),repr(plotIndex)))
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    if type(showimage) != bool:
        raise Exception("showimage must be an boolean")
    setst = __plotms_p.SetToggle( )
    setst.state = showimage
    setst.update = updateImmediately
    setst.index = plotIndex
    stub( ).setShowImage(setst)

def setShowCurve( showatm=False, showtsky=False, showimage=False, updateImmediately=True, plotIndex=0):
    setShowAtm( showatm, False, plotIndex )
    setShowTsky( showtsky, False, plotIndex )
    setShowImage( showimage, updateImmediately, plotIndex )

def __set_selection( field="", spw="", timerange="", uvrange="", antenna="", scan="", corr="", array="",
                        observation="", intent="", feed="", msselect="", updateImmediately=True, plotIndex=0 ):
    if type(field) != str:
        raise Exception("field must be a string")
    if type(spw) != str:
        raise Exception("spw must be a string")
    if type(timerange) != str:
        raise Exception("timerange must be a string")
    if type(uvrange) != str:
        raise Exception("uvrange must be a string")
    if type(antenna) != str:
        raise Exception("antenna must be a string")
    if type(scan) != str:
        raise Exception("scan must be a string")
    if type(corr) != str:
        raise Exception("corr must be a string")
    if type(array) != str:
        raise Exception("array must be a string")
    if type(observation) != str:
        raise Exception("observation must be a string")
    if type(intent) != str:
        raise Exception("intent must be a string")
    if type(feed) != str:
        raise Exception("feed must be a string")
    if type(msselect) != str:
        raise Exception("msselect must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setps = __plotms_p.SetSelection( )
    setps.field = field
    setps.spw = spw
    setps.timerange = timerange
    setps.uvrange = uvrange
    setps.antenna = antenna
    setps.scan = scan
    setps.corr = corr
    setps.array = array
    setps.observation= observation
    setps.intent = intent
    setps.feed = feed
    setps.msselect = msselect
    setps.update = updateImmediately
    setps.index = plotIndex
    return setps

def setPlotMSSelection( field="", spw="", timerange="", uvrange="", antenna="", scan="", corr="", array="",
                        observation="", intent="", feed="", msselect="", updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSSelection(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(field), repr(spw), repr(timerange), repr(uvrange), repr(antenna), repr(scan), repr(corr), repr(array), repr(observation), repr(intent), repr(feed), repr(msselect), repr(updateImmediately), repr(plotIndex)))
    stub( ).setPlotMSSelection( __set_selection( field,spw,timerange,uvrange,antenna,scan,corr,array,
                                                 observation,intent,feed,msselect,updateImmediately,plotIndex ))

def setPlotMSAveraging( channel="", time="", scan=False, field=False, baseline=False, antenna=False,
                        spw=False, scalar=False, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSAveraging(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(channel), repr(time), repr(scan), repr(field), repr(baseline), repr(antenna), repr(spw), repr(scalar), repr(updateImmediately), repr(plotIndex)))
    if type(channel) != str:
        raise Exception("channel must be a string")
    if type(time) != str:
        raise Exception("time must be a string")
    if type(scan) != bool:
        raise Exception("scan must be a bool")
    if type(field) != bool:
        raise Exception("field must be a bool")
    if type(baseline) != bool:
        raise Exception("baseline must be a bool")
    if type(antenna) != bool:
        raise Exception("antenna must be a bool")
    if type(spw) != bool:
        raise Exception("spw must be a bool")
    if type(scalar) != bool:
        raise Exception("scalar must be a bool")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setpa = __plotms_p.SetAveraging( )
    setpa.channel = channel
    setpa.time = time
    setpa.scan = scan
    setpa.field = field
    setpa.baseline = baseline
    setpa.antenna = antenna
    setpa.spw = spw
    setpa.scalar = scalar
    setpa.update = updateImmediately
    setpa.index = plotIndex
    stub( ).setPlotMSAveraging(setpa)

def setPlotMSTransformations( freqframe="", veldef="", restfreq="", xshift=0.0,
                              yshift=0.0, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSTransformations(%s,%s,%s,%s,%s,%s,%s)" % (repr(freqframe), repr(veldef), repr(restfreq), repr(xshift), repr(yshift), repr(updateImmediately), repr(plotIndex)))
    if type(freqframe) != str:
        raise Exception("freqframe must be a string")
    if type(veldef) != str:
        raise Exception("veldef must be a string")
    if type(restfreq) != str:
        raise Exception("restfreq must be a string")
    if not isinstance(xshift,_real_t):
        raise Exception("xshift must be a real number")
    if not isinstance(yshift,_real_t):
        raise Exception("yshift must be a real number")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setpt = __plotms_p.SetTransform( )
    setpt.freqframe = freqframe
    setpt.veldef = veldef
    setpt.restfreq = restfreq
    setpt.xshift = float(xshift)
    setpt.yshift = float(yshift)
    setpt.update = updateImmediately
    setpt.index = plotIndex
    stub( ).setPlotMSTransformations(setpt)

def setPlotMSCalibration( use=False, callibrary="", updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSCalibration(%s,%s,%s,%s)" % (repr(use), repr(callibrary), repr(updateImmediately), repr(plotIndex)))
    if type(use) != bool:
        raise Exception("use must be a boolean")
    if type(callibrary) != str:
        raise Exception("callibrary must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setpc = __plotms_p.SetCalibration( )
    setpc.uselib = use
    setpc.callib = callibrary
    setpc.index = plotIndex
    setpc.update = updateImmediately
    stub( ).setPlotMSCalibration(setpc)

def setFlagExtension( extend=False, correlation="", channel=False, spw=False, antenna="", time=False,
                      scans=False, field=False, alternateSelection={} ):
    if (debug): print("<debug>          pm.setFlagExtension(%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(extend), repr(correlation), repr(channel), repr(spw), repr(antenna), repr(time), repr(scans), repr(field), repr(alternateSelection)))
    if type(extend) != bool:
        raise Exception("extend must be a boolean")
    if type(correlation) != str:
        raise Exception("correlation must be a string")
    if type(channel) != bool:
        raise Exception("channel must be a boolean")
    if type(spw) != bool:
        raise Exception("spw must be a boolean")
    if type(antenna) != str:
        raise Exception("antenna must be a string")
    if type(time) != bool:
        raise Exception("time must be a boolean")
    if type(scans) != bool:
        raise Exception("scans must be a boolean")
    if type(field) != bool:
        raise Exception("field must be a boolean")
    if type(alternateSelection) != dict:
        raise Exception("alternateSelection must be a record")
    setfe = __plotms_p.SetFlagExtension( )
    setfe.extend = extend
    setfe.correlation = correlation
    setfe.channel = channel
    setfe.spw = spw
    setfe.antenna = antenna
    setfe.time = time
    setfe.scans = scans
    setfe.field = field
    setfe.use_alternative = (len(alternateSelection) > 0)
    if setfe.use_alternative:
        sel = alternateSelection
        setfe.alternative_selection.CopyFrom( __set_selection(
            sel["field"] if "field" in sel else "",
            sel["spw"] if "spw" in sel else "",
            sel["timerange"] if "timerange" in sel else "",
            sel["uvrange"] if "uvrange" in sel else "",
            sel["antenna"] if "antenna" in sel else "",
            sel["scan"] if "scan" in sel else "",
            sel["corr"] if "corr" in sel else "",
            sel["array"] if "array" in sel else "",
            sel["observation"] if "observation" in sel else "",
            sel["intent"] if "intent" in sel else "",
            sel["feed"] if "feed" in sel else "",
            sel["msselect"] if "msselect" in sel else "",
            sel["updateImmediately"] if "updateImmediately" in sel else True,
            sel["plotIndex"] if "plotIndex" in sel else 0 ) )
    stub( ).setFlagExtension(setfe)

def setExportRange( range="" ):
    if (debug): print("<debug>          pm.setExportRange(%s)" % (repr(range)))
    if type(range) != str:
        raise Exception("range must be a string")
    seter = __plotms_p.ExportRange( )
    seter.value = range
    stub( ).setExportRange(seter)

def setPlotMSIterate( iteraxis="", rowIndex=0, colIndex=0, xselfscale=False, yselfscale=False,
                      commonAxisX=False, commonAxisY=False, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSIterate(%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(iteraxis), repr(rowIndex), repr(colIndex), repr(xselfscale), repr(yselfscale), repr(commonAxisX), repr(commonAxisY), repr(updateImmediately), repr(plotIndex)))
    if type(iteraxis) != str:
        raise Exception("iteraxis must be a string")
    if type(rowIndex) != int:
        raise Exception("rowIndex must be an integer")
    if type(colIndex) != int:
        raise Exception("colIndex must be an integer")
    if type(xselfscale) != bool:
        raise Exception("xselfscale must be a boolean")
    if type(yselfscale) != bool:
        raise Exception("yselfscale must be a boolean")
    if type(commonAxisX) != bool:
        raise Exception("commonAxisX must be a boolean")
    if type(commonAxisY) != bool:
        raise Exception("commonAxisY must be a boolean")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    seti = __plotms_p.SetIterate( )
    seti.iteraxis = iteraxis
    seti.rowindex = rowIndex
    seti.colindex = colIndex
    seti.xselfscale = xselfscale
    seti.yselfscale = yselfscale
    seti.commonaxisx = commonAxisX
    seti.commonaxisy = commonAxisY
    seti.update = updateImmediately
    seti.index = plotIndex
    stub( ).setPlotMSIterate(seti)

def setColorAxis( coloraxis, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setColorAxis(%s,%s,%s)" % (repr(coloraxis), repr(updateImmediately), repr(plotIndex)))
    if type(coloraxis) != str:
        raise Exception("coloraxis must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setst = __plotms_p.SetString( )
    setst.value = coloraxis
    setst.index = plotIndex
    setst.update = updateImmediately
    stub( ).setColorAxis(setst)

def setSymbol( shape="autoscaling", size=2, color="0000ff", fill="fill", outline=False,
               updateImmediately=True, plotIndex=0, dataIndex=0 ):
    if (debug): print("<debug>          pm.setSymbol(%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(shape), repr(size), repr(color), repr(fill), repr(outline), repr(updateImmediately), repr(plotIndex), repr(dataIndex)))
    if type(shape) != str:
        raise Exception("shape must be a string")
    if type(size) != int:
        raise Exception("size must be a string")
    if type(color) != str:
        raise Exception("color must be a string")
    if type(fill) != str:
        raise Exception("fill must be a string")
    if type(outline) != bool:
        raise Exception("outline must be a boolean")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    if type(dataIndex) != int:
        raise Exception("dataIndex must be an integer")
    setsy = __plotms_p.SetSymbol( )
    setsy.shape = shape
    setsy.size = size
    setsy.color = color
    setsy.fill = fill
    setsy.outline = outline
    setsy.update = updateImmediately
    setsy.index = plotIndex
    setsy.dataindex = dataIndex
    stub( ).setSymbol(setsy)

def setFlaggedSymbol( shape="nosymbol", size=2, color="ff0000", fill="fill", outline=False,
                      updateImmediately=True, plotIndex=0, dataIndex=0 ):
    if (debug): print("<debug>          pm.setFlaggedSymbol(%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(shape), repr(size), repr(color), repr(fill), repr(outline), repr(updateImmediately), repr(plotIndex), repr(dataIndex)))
    if type(shape) != str:
        raise Exception("shape must be a string")
    if type(size) != int:
        raise Exception("size must be a string")
    if type(color) != str:
        raise Exception("color must be a string")
    if type(fill) != str:
        raise Exception("fill must be a string")
    if type(outline) != bool:
        raise Exception("outline must be a boolean")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    if type(dataIndex) != int:
        raise Exception("dataIndex must be an integer")
    setsy = __plotms_p.SetSymbol( )
    setsy.shape = shape
    setsy.size = size
    setsy.color = color
    setsy.fill = fill
    setsy.outline = outline
    setsy.update = updateImmediately
    setsy.index = plotIndex
    setsy.dataindex = dataIndex
    stub( ).setFlaggedSymbol(setsy)

def setConnect( xconnector="none", timeconnector=False, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setConnect(%s,%s,%s,%s)" % (repr(xconnector), repr(timeconnector), repr(updateImmediately), repr(plotIndex)))
    if type(xconnector) != str:
        raise Exception("xconnector must be a string")
    if type(timeconnector) != bool:
        raise Exception("timeconnector must be a boolean")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setcn = __plotms_p.SetConnect( )
    setcn.xconnector = xconnector
    setcn.timeconnector = timeconnector
    setcn.update = updateImmediately
    setcn.index = plotIndex
    stub( ).setConnect(setcn)

def setLegend( showLegend=False, legendPosition="upperright", updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setLegend(%s,%s,%s,%s)" % (repr(showLegend), repr(legendPosition), repr(updateImmediately), repr(plotIndex)))
    if type(showLegend) != bool:
        raise Exception("showLegend must be a boolean")
    if type(legendPosition) != str:
        raise Exception("legendPosition must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setlg = __plotms_p.SetLegend( )
    setlg.show = showLegend
    setlg.position = legendPosition
    setlg.update = updateImmediately
    setlg.index = plotIndex
    stub( ).setLegend(setlg)

def setTitle( text="", updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setTitle(%s,%s,%s)" % (repr(text), repr(updateImmediately), repr(plotIndex)))
    if type(text) != str:
        raise Exception("text must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setst = __plotms_p.SetString( )
    setst.value = text
    setst.index = plotIndex
    setst.update = updateImmediately
    stub( ).setTitle(setst)

def setXAxisLabel( text="", updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setXAxisLabel(%s,%s,%s)" % (repr(text), repr(updateImmediately), repr(plotIndex)))
    if type(text) != str:
        raise Exception("text must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setst = __plotms_p.SetString( )
    setst.value = text
    setst.index = plotIndex
    setst.update = updateImmediately
    stub( ).setXAxisLabel(setst)

def setYAxisLabel( text="", updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setYAxisLabel(%s,%s,%s)" % (repr(text), repr(updateImmediately), repr(plotIndex)))
    if type(text) != str:
        raise Exception("text must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setst = __plotms_p.SetString( )
    setst.value = text
    setst.index = plotIndex
    setst.update = updateImmediately
    stub( ).setYAxisLabel(setst)

def setTitleFont( size=0, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setTitleFont(%s,%s,%s)" % (repr(size), repr(updateImmediately), repr(plotIndex)))
    if type(size) != int:
        raise Exception("size must be a integer")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setin = __plotms_p.SetInt( )
    setin.value = size
    setin.index = plotIndex
    setin.update = updateImmediately
    stub( ).setTitleFont(setin)
    
def setXAxisFont( size=0, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setXAxisFont(%s,%s,%s)" % (repr(size), repr(updateImmediately), repr(plotIndex)))
    if type(size) != int:
        raise Exception("size must be a integer")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setin = __plotms_p.SetInt( )
    setin.value = size
    setin.index = plotIndex
    setin.update = updateImmediately
    stub( ).setXAxisFont(setin)

def setYAxisFont( size=0, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setYAxisFont(%s,%s,%s)" % (repr(size), repr(updateImmediately), repr(plotIndex)))
    if type(size) != int:
        raise Exception("size must be a integer")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setin = __plotms_p.SetInt( )
    setin.value = size
    setin.index = plotIndex
    setin.update = updateImmediately
    stub( ).setYAxisFont(setin)

def setGridParams( showmajorgrid=False, majorwidth=1, majorstyle="solid", majorcolor="B0B0B0",
                   showminorgrid=False, minorwidth=1, minorstyle="solid", minorcolor="C0CCE0",
                   updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setGridParams(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (repr(showmajorgrid), repr(majorwidth), repr(majorstyle), repr(majorcolor), repr(showminorgrid), repr(minorwidth), repr(minorstyle), repr(minorcolor), repr(updateImmediately), repr(plotIndex)))
    if type(showmajorgrid) != bool:
        raise Exception("showmajorgrid must be a boolean")
    if type(majorwidth) != int:
        raise Exception("majorwidth must be an integer")
    if type(majorstyle) != str:
        raise Exception("majorstyle must be a string")
    if type(majorcolor) != str:
        raise Exception("majorcolor must be a string")
    if type(showminorgrid) != bool:
        raise Exception("showminorgrid must be a boolean")
    if type(minorwidth) != int:
        raise Exception("minorwidth must be an integer")
    if type(minorstyle) != str:
        raise Exception("minorstyle must be a string")
    if type(minorcolor) != str:
        raise Exception("minorcolor must be a string")
    setgp = __plotms_p.SetGrid( )
    setgp.showmajor = showmajorgrid
    setgp.majorwidth = majorwidth
    setgp.majorstyle = majorstyle
    setgp.minorcolor = minorcolor
    setgp.showminor = showminorgrid
    setgp.minorwidth = minorwidth
    setgp.minorstyle = minorstyle
    setgp.minorcolor = minorcolor
    stub( ).setGridParams(setgp)

def setXRange( xautorange=True, xmin=0.0, xmax=0.0, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setXRange(%s,%s,%s,%s,%s)" % (repr(xautorange), repr(xmin), repr(xmax), repr(updateImmediately), repr(plotIndex)))
    if type(xautorange) != bool:
        raise Exception("xautorange must be a boolean")
    if type(xmin) != float:
        raise Exception("xmin must be a float")
    if type(xmax) != float:
        raise Exception("xmax must be a float")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setrg = __plotms_p.SetRange( )
    setrg.automatic = xautorange
    setrg.min = xmin
    setrg.max = xmax
    setrg.index = plotIndex
    setrg.update = updateImmediately
    stub( ).setXRange(setrg)

def setYRange( yautorange=True, ymin=0.0, ymax=0.0, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setYRange(%s,%s,%s,%s,%s)" % (repr(yautorange), repr(ymin), repr(ymax), repr(updateImmediately), repr(plotIndex)))
    if type(yautorange) != bool:
        raise Exception("yautorange must be a boolean")
    if type(ymin) != float:
        raise Exception("ymin must be a float")
    if type(ymax) != float:
        raise Exception("ymax must be a float")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setrg = __plotms_p.SetRange( )
    setrg.automatic = yautorange
    setrg.min = ymin
    setrg.max = ymax
    setrg.index = plotIndex
    setrg.update = updateImmediately
    stub( ).setYRange(setrg)

def setPlotMSPageHeaderItems( pageHeaderItems, updateImmediately=True, plotIndex=0 ):
    if (debug): print("<debug>          pm.setPlotMSPageHeaderItems(%s,%s,%s)" % (repr(pageHeaderItems), repr(updateImmediately), repr(plotIndex)))
    if type(pageHeaderItems) != str:
        raise Exception("pageHeaderItems must be a string")
    if type(updateImmediately) != bool:
        raise Exception("updateImmediately must be a boolean")
    if type(plotIndex) != int:
        raise Exception("plotIndex must be an integer")
    setst = __plotms_p.SetString( )
    setst.value = pageHeaderItems
    setst.index = plotIndex
    setst.update = updateImmediately
    stub( ).setPlotMSPageHeaderItems(setst)

def save( plotfile, format, verbose=True, highres=False, dpi=-1, width=-1, height=-1 ):
    if (debug): print("<debug>          pm.save(%s,%s,%s,%s,%s,%s,%s)" % (repr(plotfile), repr(format), repr(verbose), repr(highres), repr(dpi), repr(width), repr(height)))
    if type(plotfile) != str:
        raise Exception("plotfile must be a string")
    if type(format) != str:
        raise Exception("format must be a string")
    if type(verbose) != bool:
        raise Exception("verbose must be a boolean")
    if type(highres) != bool:
        raise Exception("highres must be a boolean")
    if type(dpi) != int:
        raise Exception("dpi must be an integer")
    if type(width) != int:
        raise Exception("width must be an integer")
    if type(height) != int:
        raise Exception("height must be an integer")
    sv = __plotms_p.Save( )
    sv.path = plotfile
    sv.format = format
    sv.verbose = verbose
    sv.highres = highres
    sv.dpi = dpi
    sv.width = width
    sv.height = height
    stub( ).save(sv)

def update( ):
    if (debug): print("<debug>          pm.update( )")
    # CASA 5 tool returns a bool upon success
    # grpc includes an error option...
    stub( ).update(__empty_p.Empty( ))
    return True
