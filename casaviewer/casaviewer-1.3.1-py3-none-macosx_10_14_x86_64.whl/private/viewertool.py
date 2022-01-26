import os as __os
import sys as __sys
import pwd as __pwd
import time as __time
import traceback
from .config import app_path

debug = 'GRPC_DEBUG' in __os.environ

###
### TODO:   (1) perhaps add __main__ which execs casaviewer app
###             https://stackoverflow.com/a/55346918
###

###
### Load the necessary gRPC libraries and bindings.
###
### The generated wrappers assume that all of the wrappers can be
### loaded using the standard sys.path so here we add the path to
### the wrappers, load all of the needed wrappers, and then remove
### the private path from sys.path
###
__sys.path.insert(0, __os.path.dirname(__os.path.abspath(__file__)))
import grpc as __grpc
from . import shutdown_pb2_grpc as __sd
from . import ping_pb2_grpc as __ping
from google.protobuf import empty_pb2 as __empty_p
from . import img_pb2 as __img_p
from . import img_pb2_grpc as __img_rpc
__sys.path.pop(0)

###
### Tried to subclass to add __hash__( ) function to Id message (needed
### to be able to build a dict of Ids), but got error "TypeError: A
### Message class can only inherit from Message". At first I assumed
### this must be Google (gRPC) trying to add some structure to Python,
### but after brief searching, it seems like just Python brokenness...
###
def __h(id):
    return id.id

def make_id(v):
    i = __img_p.Id( )
    i.id = v
    return i

def is_id(o):
    ### "type(o) == __img_p.Id"   fails...
    return o.__class__.__name__ == __img_p.Id.__name__ and o.__class__.__module__ == __img_p.Id.__module__

__proc = { '--server': None, '--nogui': None }
__stub =    { '--server': None, '--nogui': None }
__channel = { '--server': None, '--nogui': None }
__uri = { '--server': None, '--nogui': None }
__stub_id =    { '--server': None, '--nogui': None }
__health_check = { '--server': 0, '--nogui': 0 }
__id_gui_state = { }
__registered = False
__try_check_health = True

###
### When casaviewer is started (via __launch) without casatools, this function
### is called to shutdown the casaviewer app when the user exits python.
###
def __shutdown_sans_casatools( ):
    global __uri
    for k in __uri:
        if __uri[k] is not None:
            channel = __grpc.insecure_channel(__uri[k])
            shutdown = __sd.ShutdownStub(channel)
            shutdown.now(__empty_p.Empty( ))

###
### A named-pipe is used for communication when casaviewer is started
### without casatools. The --server=... flag to the casaviewer app
### accepts wither a named pipe (path) or a gRPC URI. The URI for
### the casaviewer app is passed back through the named pipe.
###
def __fifo_name(index):
    count = 0
    path = "/tmp/._casaviewer_%s_%s_%s_" % (__pwd.getpwuid(__os.getuid()).pw_name, __os.getpid( ), count)
    while __os.path.exists(path):
        count = count + 1
        path = "/tmp/._casaviewer_%s_%s_%s_" % (__pwd.getpwuid(__os.getuid()).pw_name, __os.getpid( ), count)
    return path

###
### Create a named pipe...
###
def __mkfifo( ):
    path =  __fifo_name(0)
    __os.mkfifo(path)
    return path

###
### Launch the casaviewer app in either the casatools context (gRPC URI)
### or the stand-alone context (named pipe).
###
def __launch(server="--server"):
    from subprocess import Popen, STDOUT
    import argparse as _argparse
    global __proc
    global __uri
    np_path = None

    # need to fetch any --rcdir and --nogui from __sys.argv
    parse = _argparse.ArgumentParser(add_help=False)
    parse.add_argument("--rcdir",dest='rcdir',default=None)
    parse.add_argument("--nogui",dest='nogui',action='store_const',const=True,default=False)
    _flags,_args = parse.parse_known_args(__sys.argv)

    rcdir = [ ]
    if _flags.rcdir is not None:
        rcdir = [ "--rcdir=%s" % __os.path.expanduser(_flags.rcdir) ]

    nogui = [ ]
    if _flags.nogui:
        nogui = [ "--nogui" ]

    data_path = [ ]
    try:
        from casatools import ctsys as ct
        data_path = [ "--datapath=%s" % ct.rundata( ) ]
    except: pass

    if __uri[server] is None or __proc[server] is None:
        try:
            from casatasks import casalog
            from casatools import ctsys

            with open(__os.devnull, 'r+b', 0) as DEVNULL:
                __proc[server] = Popen( [ app_path,
                                          '--casalogfile=%s' % casalog.logfile( ),
                                          '%s=%s' % (server,ctsys.registry( )['uri']) ] + data_path + rcdir + nogui,
#                                       stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT,
#                                       stdin=DEVNULL, stdout=STDOUT, stderr=STDOUT,
                                        close_fds=True,
                                        env={k:v for k,v in __os.environ.copy().items() if 'MPI' not in k} )
            __time.sleep(2)						# give it a second to launch
            count = 0
            while __uri[server] is None and count < 50:			# search for registered viewer
                print("(%s) waiting for viewer process..." % count)
                for k,v in ctsys.services( ).items( ):
                    if 'id' in v:
                        print("\t...%s" % repr(v))
                        id = v['id'].split(':')[0]
                        if id == 'casaviewer':
                            if debug: print("located casaviewer... %s" % v['id'])
                            __uri[server] = v['uri']
                            __stub_id[server] = v['id']
                            break
                count = count + 1
                __time.sleep(1)
            if __uri[server] is None:
                print("could not sync with casaviewer...")
        except ModuleNotFoundError:
            try:
                np_path = __mkfifo( )
                with open(__os.devnull, 'r+b', 0) as DEVNULL:
#                    __proc = Popen( [ app_path, '%s=%s' % (server,np_path) ],
#                                    stdin=DEVNULL, stdout=STDOUT, stderr=STDOUT,
#                                    close_fds=True )
                    __proc[server] = Popen( [ app_path, '--casalogfile=%s' % casalog.logfile(),
                                              '%s=%s' % (server,np_path) ] + data_path + rcdir + nogui,
                                            env={k:v for k,v in __os.environ.copy().items() if 'MPI' not in k} )

                with open( np_path, 'r' ) as input:
                    __uri[server] = input.readline( ).rstrip( )
                print("casaviewer: %s" % __uri[server])
                __os.remove(np_path)
                global __registered
                if not __registered:
                    import atexit
                    atexit.register(__shutdown_sans_casatools)
                    __registered = True
            except:
                print("error: casaviewer launch failed...")
                __uri[server] = None
                __os.remove(np_path)
    return __uri[server]

def __extract_region_box( reg ):
    if 'regions' in reg :
        if type(reg['regions']) != dict or '*1' not in reg['regions'] :
            raise Exception("invalid region, has 'regions' field but wrong format")
        reg=reg['regions']['*1']

    if 'trc' not in reg or 'blc' not in reg :
        raise Exception("region must have a 'blc' and 'trc' field")

    blc_r = reg['blc']
    trc_r = reg['trc']

    if type(blc_r) != dict or type(trc_r) != dict :
        raise Exception("region blc/trc of wrong type")

    blc_k = list(blc_r.keys( ))
    trc_k = list(trc_r.keys( ))

    if len(blc_k) < 2 or len(trc_k) < 2:
        raise Exception("degenerate region")

    blc_k.sort( )
    trc_k.sort( )

    if type(blc_r[blc_k[0]]) != dict or type(blc_r[blc_k[1]]) != dict or \
           type(trc_r[trc_k[0]]) != dict or type(trc_r[trc_k[1]]) != dict :
        raise Exception("invalid blc/trc in region")

    if 'value' not in blc_r[blc_k[0]] or 'value' not in blc_r[blc_k[1]] or \
           'value' not in trc_r[trc_k[0]] or 'value' not in trc_r[trc_k[1]]:
        raise Exception("invalid shape for blc/trc in region")

    if (type(blc_r[blc_k[0]]['value']) != float and type(blc_r[blc_k[0]]['value']) != int) or \
           (type(blc_r[blc_k[1]]['value']) != float and type(blc_r[blc_k[1]]['value']) != int) or \
           (type(trc_r[trc_k[0]]['value']) != float and type(trc_r[trc_k[0]]['value']) != int) or \
           (type(trc_r[trc_k[0]]['value']) != float and type(trc_r[trc_k[0]]['value']) != int) :
        raise Exception("invalid type for blc/trc value in region")

    blc = [ float(blc_r[blc_k[0]]['value']), float(blc_r[blc_k[1]]['value']) ]
    trc = [ float(trc_r[trc_k[0]]['value']), float(trc_r[trc_k[1]]['value']) ]

    coord = "pixel"
    if 'name' in reg and reg['name'] == "WCBox":
        coord = "world"

    return ( blc, trc, coord )

def __stub_check(serv_str):
    from time import time
    global __stub, __health_check, __proc, __try_check_health
    s = __stub[serv_str]
    if s is None:
        raise RuntimeError("invalid service string")
    else:
        cur = time( )
        if __try_check_health:
            __health_check[serv_str] = cur
            try:
                channel = __grpc.insecure_channel(__uri[serv_str])
                ping = __ping.PingStub(channel)
                if debug: print("pinging viewer...")
                ping.now(__empty_p.Empty( ),timeout=5)
                if debug: print("viewer responded to ping...")
                return s
            except:
                from casatasks import casalog
                from casatools import ctsys
                print("viewer did not responded to ping... restarting...")
                __proc[serv_str].kill( )
                __proc[serv_str] = None
                __stub[serv_str] = None
                # unregister presumed defunct casaviewer process...
                casalog.origin('viewertool')
                if ctsys.remove_service( __uri[serv_str] ):
                    casalog.post("successfully removed defunct viewer: %s" % __uri[serv_str])
                    __uri[serv_str] = None
                else:
                    casalog.post("failed to remove defunct viewer: %s" % __uri[serv_str])
                    __try_check_health = False

                return stub(True if serv_str == "--server" else False)
        else:
            return s

###
### Get the casaviewer app proxy; if the casaviewer app has not been
### launched, then the first time stub is called it will launch the
### casaviewer app and create the stub either by reading the app's
### URI through a named pipe or retrieving it from the casatools
### registry.
###
def stub(context={}):
    global __stub, __channel
    if type(context) is bool:
        serv_str = "--server" if context else "--nogui"
        if __stub[serv_str] is None:
            uri = __launch(serv_str)
            if uri is None:
                print("error: casaviewer launch failed...")
            else:
                __channel[serv_str] = __grpc.insecure_channel(uri)
                __stub[serv_str]    = __img_rpc.viewStub(__channel[serv_str])
        return __stub_check(serv_str)
    elif is_id(context):
        if __h(context) in __id_gui_state:
            serv_str = "--server" if __id_gui_state[__h(context)] else "--nogui"
            return __stub_check(serv_str)
        elif panel == make_id(0):
            return stub(True)
        else:
            raise Exception("Id %s not found" % context)
    else:
        raise Exception("context must either be a boolean or an id")

###
### Get/set viewer's current working directory...
###
def cwd( new_path='', gui=True ):
    if type(new_path) != str:
        raise Exception("cwd() takes a single (optional) string...")
    if type(gui) != bool:
        raise Exception("gui parameter should be a boolean")
    if gui is False and __sys.platform != 'linux':
        raise Exception("non-gui operation is only supported on Linux")
    pin = __img_p.Path( )
    pin.path = new_path
    return stub(gui).cwd(pin).path

###
### get the type of a particular file/dir
###
def fileinfo( path, gui=True ):
    if type(path) != str:
        raise Exception("fileinfo() takes a single path...")
    if type(gui) != bool:
        raise Exception("gui parameter should be a boolean")
    if gui is False and __sys.platform != 'linux':
        raise Exception("non-gui operation is only supported on Linux")
    pin = __img_p.Path( )
    pin.path = path
    return stub(gui).fileinfo(pin).type

###
### get info about a casaviewer id
###
def keyinfo( key ):
    if not is_id(key):
        raise Exception("keyinfo() takes a casaviewer id...")
    return stub(key).keyinfo(key).type

###
### Create a new panel in the casaviewer app... returns panel id
###
def panel( paneltype="viewer", gui=True ) :
    if type(paneltype) != str or (paneltype != "viewer" and paneltype != "clean"):
        if not (paneltype.endswith('.rstr') and __os.path.isfile(paneltype)):
            raise Exception("the only valid panel types are 'viewer' and 'clean' or path to restore file")
    if type(gui) != bool:
        raise Exception("gui parameter should be a boolean")
    if gui is False and __sys.platform != 'linux':
        raise Exception("non-gui operation is only supported on Linux")

    panel_req = __img_p.NewPanel( )
    panel_req.hidden = False
    panel_req.type = paneltype
    result = stub(gui).panel(panel_req)
    if result is not None:
        __id_gui_state[__h(result)] = gui
    return result

###
### load data into a panel... returns data id
###
def load( path, displaytype="raster", panel=make_id(0), scaling=0 ):
    if type(path) != str or type(displaytype) != str or \
       (type(scaling) != float and not is_id(panel)) :
            raise Exception("load() takes two strings; only the first arg is required...")
    nd = __img_p.NewData( )
    nd.panel.CopyFrom(panel)
    nd.path = path
    nd.type = displaytype
    nd.scale = scaling
    result = stub(panel).load(nd)
    if result is not None:
        __id_gui_state[__h(result)] = __id_gui_state[__h(panel)]
    return result

###
### close panel... no return value
###
def close( panel=make_id(0) ):
    if not is_id(panel) :
        raise Exception("close() takes one optional integer...")
    stub(panel).close(panel)

###
### set data range to data which should be [min, max]... no return vaue
###
def datarange( range, data=make_id(0) ):
    if type(range) != list or not is_id(data) or \
       all( map( lambda x: type(x) == int or type(x) == float, range ) ) == False:
        raise Exception("datarange() takes (numeric list,int)...")
    if len(range) != 2 or range[0] > range[1] :
        raise Exception("range should be [ min, max ]...")
    rng = __img_p.DataRange( )
    rng.data.CopyFrom(data)
    rng.min = range[0]
    rng.max = range[1]
    stub(data).datarange(rng)

###
### set the channel that is displayed... no return value
###
def channel( num=-1, panel=make_id(0) ):
    if type(num) != int or not is_id(panel):
        raise Exception("frame() takes (int,id); each argument is optional...")
    sc = __img_p.SetChannel( )
    sc.panel.CopyFrom(panel)
    sc.number = num
    stub(panel).channel(sc)

###
### set colormap for a particular panel... no return value
###
def colormap( map, data_or_panel=make_id(0) ):
    if type(map) != str or not is_id(data_or_panel):
        raise Exception("colormap() takes a colormap name and an optional panel or data id...")
    cm = __img_p.ColorMap( )
    cm.id.CopyFrom(data_or_panel)
    cm.map = map
    stub(data_or_panel).colormap(cm)

###
### show or hide colorwedge... no return value
###
def colorwedge( show, data_or_panel=make_id(0) ):
    if type(show) != bool or not is_id(data_or_panel):
        raise Exception("colorwedge() takes a boolean and an optional panel or data id...")
    cw = __img_p.Toggle( )
    cw.id.CopyFrom(data_or_panel)
    cw.state = show
    stub(data_or_panel).colorwedge(cw)

###
### freeze gui for multiple changes... no return value
###
def freeze( panel=make_id(0) ):
    if not is_id(panel) :
        raise Exception("freeze() takes only a panel id...")
    stub(panel).freeze(panel)
###
### unfreeze gui after multiple changes... no return value
###
def unfreeze( panel=make_id(0) ):
    if not is_id(panel) :
        raise Exception("unfreeze() takes only a panel id...")
    stub(panel).unfreeze(panel)

###
### popup gui tool... no return value
###
def popup( what, panel=make_id(0) ):
    if type(what) != str or not is_id(panel):
        raise Exception("popup() takes a string followed by one optional integer...")
    pu = __img_p.PopUp( )
    pu.panel.CopyFrom(panel)
    pu.name = what
    stub(panel).popup(pu)

###
### restore restore file to a new panel... returns id
###
def restore( path, panel=make_id(0) ):
    if type(path) != str or not is_id(panel):
        ### probably should check for file existence
        raise Exception("restore() takes a string and an integer; only the first arg is required...")
    rs = __img_p.Restore( )
    rs.panel.CopyFrom(panel)
    rs.path = path
    result = stub(panel).restore(rs)
    if result is not None:
        __id_gui_state[__h(result)] = __id_gui_state[__h(panel)]
    return result

###
### generate an output file... no return value
###
def output( device, devicetype='file', panel=make_id(0), scale=1.0, dpi=300, format="jpg", \
            orientation="portrait", media="letter" ):
    if type(device) != str or not is_id(panel) or type(scale) != float or \
       type(dpi) != int or type(format) != str or type(orientation) != str or type( media ) != str:
        raise Exception("output() takes (str,int,float,int,str,str,str); only the first is required...")
    out = __img_p.Output( )
    out.panel.CopyFrom(panel)
    out.device = device
    out.devicetype = devicetype
    out.orientation = orientation
    out.media = media
    out.format = format
    out.scale = scale
    out.dpi = dpi
    stub(panel).output(out)

###
### set axes... no return value
###
def axes( x='', y='', z='', panel=make_id(0) ):
    if type(x) != str or type(y) != str or type(z) != str or not is_id(panel) :
        raise Exception("axes() takes one to three strings and an optional panel id...")
    ax = __img_p.Axes( )
    ax.panel.CopyFrom(panel)
    ax.x = x
    ax.y = y
    ax.z = z
    stub(panel).axes(ax)

###
### set contour levels... no return value
###
def contourlevels( levels=[], baselevel=2147483648.0, unitlevel=2147483648.0, data=make_id(0) ):
    if type(levels) != list or not is_id(data) or \
       all( map( lambda x: type(x) == int or type(x) == float, levels ) ) == False:
        raise Exception("contorlevels() takes (numeric list,id)...")
    cl = __img_p.ContourLevels( )
    cl.id.CopyFrom(data)
    cl.levels.extend(levels)
    cl.baselevel = baselevel
    cl.unitlevel = unitlevel
    stub(data).contourlevels(cl)

###
### set the contour color... no return value
###
def contourcolor( color="foreground", data=make_id(0) ):
    if type(color) != str or not is_id(data):
        raise Exception("contorcolor() takes color name and data id...")
    cc = __img_p.ContourColor( )
    cc.id.CopyFrom(data)
    cc.color = color
    stub(data).contourcolor(cc)

###
### set contour thickness (0-5)...no return value
###
def contourthickness( thickness=0.0, data=make_id(0) ):
    if type(thickness) != float or not is_id(data):
        raise Exception("contourthickness() takes a float representing the thickness and data id...")
    if thickness < 0 or thickness > 5:
        raise Exception("the thickness supplied to contourthickness() should between 0 and 5")
    ct = __img_p.ContourThickness( )
    ct.id.CopyFrom(data)
    ct.thickness = thickness
    stub(data).contourthickness(ct)

###
### set the zoom level... no return value
###
def zoom( level=None, blc=[], trc=[], coordinates="pixel", region="", panel=make_id(0) ):
    if ( type(level) != int and level is not None) or \
       type(blc) != list or type(trc) != list or not is_id(panel) or \
           type(coordinates) != str or (type(region) != str and type(region) != dict) :
        raise Exception("zoom() takes (int|None,list,list,str,id); each argument is optional...")

    if (type(region) == str and __os.path.isfile( region )):
        raise Exception("zoom( ) does not yet support loading region files (but does accept a region dictionary)")
    if type(region) is dict:
        ( _blc, _trc, _coord ) = __extract_region_box( reg )
        zoom( level=None, blc=_blc, trc=_trc, coordinates=_coord, region="", panel=panel )

    if level is not None:
        zl = __img_p.SetZoomLevel( )
        zl.panel.CopyFrom(panel)
        zl.level = level
        stub(panel).zoomlevel(zl)
    else:
        if len(blc) != 2 or  len(trc) != 2:
            raise Exception("blc/tlc in zoom() should each be a list of two integers")
        zb = __img_p.SetZoomBox( )
        zb.panel.CopyFrom(panel)
        zb.blc.x = blc[0]
        zb.blc.y = blc[1]
        zb.trc.x = trc[0]
        zb.trc.y = trc[1]
        zb.coord_type = coordinates
        stub(panel).zoombox(zb)

###
### hide a panel... no return value
###
def hide( panel=make_id(0) ):
    if not is_id(panel) :
        raise Exception("hide() takes a single panel identifier ...")
    stub(panel).hide(panel)

###
### show (unhide) a panel... no return value
###
def show( panel=make_id(0) ):
    if not is_id(panel) :
        raise Exception("show() takes a single panel identifier ...")
    stub(panel).show(panel)
