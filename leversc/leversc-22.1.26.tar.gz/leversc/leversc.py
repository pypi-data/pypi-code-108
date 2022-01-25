import math
import json
import struct
import requests
import numpy as np
import os
import sys
import time
import pkgutil
import subprocess
from imageio import imread

class leversc:
    """
    A class wrapper to interface with the leversc viewer.

    This class is built to function similarly to matplotlib and Matlab's figure() function,
    the leversc object represents a single leversc viewer window with associated image metadata (imD)
    and visualization parameters. Object methods allow changing rendering parameters programatically 
    and send new images to view (with the same metadata).

    Parameters
    ----------
    im : numpy.ndarray, optional
        5-D image to send to viewer on startup, can also be sent using the show(im) method
    imD : dict, optional
        Leverjs image metadata, can be reset using the setImageData(imD) method
    figNum : int, default=1
        Figure number of the leversc viewer (default to 1)

    Raises
    ------
    TypeError
        If im is not None and is not of type numpy.ndarray

    See Also
    --------
    show: Show 5-D image in the leversc viewer
    """
    def __init__(self, im=None, imD=None, figNumber=1,strDB=None):
        self._host = "http://localhost"
        self._base_port = 3000
        self._npack = 4

        self._figNumber = figNumber
        self.setImageData(imD)
        if strDB is not None:
            self.showLEVER(strDB)
        elif im is not None:
            self.show(im)

    def setImageData(self, imD=None):
        """
        Set the image metadata associated with this viewer window.

        This function will set or reset (in the case of imD=None or no arguments) the leverjs metadata associated with
        this leversc viewer window.

        Parameters
        ----------
        imD : dict, optional
            Leverjs image metadata
            Important Keys:
                "PhysicalPixelSize" - The resolution of each pixel dimension x,y,z (generally in um)
                "ChannelNames" - The names of each channel in the image
        """        
        if imD is None:
            self._CONSTANTS={}
            self._imageData = {} 
        elif 'imageData' in imD.keys():
            # passed in a CONSTANTS struct - use CONSTANTS.imageData
            self._CONSTANTS=imD
            self._imageData = imD['imageData']
        else:
            self._CONSTANTS={}
            self._imageData = imD


    def setFigureNumber(self, figNumber):
        """
        Set the the figure number (leversc viewer) associated with this object

        Parameters
        ----------
        figNumber : int
            This is the figure number (leversc window) that the object will send images to

        Raises
        ------
        ValueError
            If figNumber is less than 1
        """
        if figNumber <= 0:
            raise ValueError("Figure number must be greater than zero")
        self._figNumber = figNumber

    def captureImage(self):
        if ( not self._check_leversc() ):
            return None
        # make sure leversc is ready
        while (not self.drawComplete()):
            time.sleep(0.1)
        # do the capture
        URL = self._leversc_url('screenCap')
        im=imread(URL)
        return im
    
    def drawComplete(self):
        URL=self._leversc_url('drawComplete')
        response=requests.get(URL)
        bComplete=response.json()
        return bComplete
    def showLEVER(self,strDB):
        """
        Open a .LEVER file in the leversc viewer

        Parameters
        ----------
        strDB : string
            /path/to/myFile.LEVER

        """
        if ( not self._check_leversc() ):
            if ( not self._init_leversc(strDB) ):
                return
        
    def show(self, im):
        """
        Show a 5-D image in the leversc viewer

        Sends a 5-D numpy array to the leversc viewer for display. Note: if the imageData has not been set
        then this method will set default imageData based on the input image.

        Parameters
        ----------
        im : numpy.ndarray
            5-D image to send to viewer

        Raises
        ------
        TypeError
            If im is not of type numpy.ndarray
        """
        if type(im) is not np.ndarray:
            raise TypeError("Image must be a numpy array")

        if len(im.shape) < 3:
            print("ERROR: 2D Images are not supported!")
            return

        # Launch leversc viewer if not alread up
        if ( not self._check_leversc() ):
            if ( not self._init_leversc() ):
                return

        # Normalize image access by creating an f_contiguous image view
        imfctg = leversc._get_fcontig_imview(im)
        if len(imfctg.shape) == 3:
            imfctg = np.expand_dims(imfctg, axis=3)
        # Normalize dimensions (make sure there are at least 4 (x,y,z,c))
        def onepad_slice(tpl, size): return (tpl + (1,)*(size-len(tpl)))
        dims = onepad_slice(imfctg.shape, 4)

        if ( len(dims) > 4 and dims[4] > 1 ):
            print('WARNING: Multi-frame images are not supported using frame 1!')
            imfctg = imfctg[:,:,:,:,0]

        # Convert im to uint8
        chmax = np.amax(np.amax(np.amax(imfctg, axis=0, keepdims=True), axis=1, keepdims=True), axis=2, keepdims=True)
        chim = ((255.0 * imfctg) / chmax).astype("uint8")

        # Setup valid imageData
        self._imageData = leversc._imd_from_im(imfctg,dims,self._imageData)

        header_json,count_packs = self._make_header(dims)

        # Multipart-post request send
        multipart = [("header", (None, header_json, "application/json"))]
        for i in range(count_packs):
            multipart.append(("lbins",("lbin%d"%(i), self._im_to_lbin(chim,dims,i), "application/octet-stream")))

        resp = requests.post(url=self._leversc_url("/loadfig"), files=multipart)

        # if we have a CONSTANTS and a renderParams, set it
        if self._CONSTANTS!={} and 'renderParams' in self._CONSTANTS.keys():
            self.renderParams=self._CONSTANTS['renderParams']


    def _im_to_lbin(self,im,dims,pidx):
        choffset = pidx * self._npack
        chsize = min(dims[3]-choffset, self._npack)

        imsub = im[:,:,:,choffset:(choffset+chsize)]
        lbin_size = 4*2 + np.prod(dims[:3])*chsize

        outbytes = bytearray(lbin_size)
        struct.pack_into("!HHHH", outbytes, 0, chsize,dims[0],dims[1],dims[2])
        imout = np.frombuffer(memoryview(outbytes)[(4*2):], "uint8")

        imout[:] = np.reshape(np.transpose(imsub, (3,0,1,2)), -1, order='F')
        return outbytes


    def _make_header(self, dims):
        count_packs = math.ceil(dims[3] / self._npack)

        # Make json metadata header
        imdjson = json.dumps(self._imageData)
        return imdjson,count_packs

    def _check_leversc(self):
        try:
            resp = requests.get(url=self._leversc_url("/info"), timeout=0.5)
        except requests.exceptions.ConnectTimeout as e:
            return False
        except requests.exceptions.ConnectionError as e:
            return False
        except Exception as e:
            print("Unable to contact leversc server: %s (%s)" % (self._leversc_url("/info"), e))
            return False
        return True


    def _leversc_url(self,reqpath):
        if ('/' != reqpath[0]):
            reqpath='/'+reqpath
        return "%s:%s%s"%(self._host,self._base_port + self._figNumber, reqpath)


    @staticmethod
    def _get_fcontig_imview(im):
        if im.flags.f_contiguous:
            return im
        else:
            imflat = np.reshape(im, -1, order='A')
            imfctg = np.reshape(imflat, im.shape[::-1], order='F')
            return imfctg


    @staticmethod
    def _get_normalized_dims(im):
        # Helper to pd im.shape out to required number of dimensions
        def _opad_slice(tpl, size): return (tpl + (1,)*(size-len(tpl)))[:size]

        # Reverse the dimension order depending of f/c_contiguous
        if im.flags.f_contiguous:
            # dims = _opad_slice(im.shape, 4)
            dims = _opad_slice(im.shape, 4)
        else:
            dims = _opad_slice(im.shape[::-1], 4)
        return dims


    @staticmethod
    def _imd_from_im(im, dims, imD):
        # Make sure every channel has a name ("Channel %i" by default)
        chnames = imD["ChannelNames"] if "ChannelNames" in imD else []
        chnames = [chnames[x] if len(chnames) > x else "Channel %s"%(x+1) for x in range(dims[3])]

        # Set valid pixel size for each x,y,z dim
        pxsize = imD["PixelPhysicalSize"] if "PixelPhysicalSize" in imD else [1,1,1]
        pxsize = [x if x > 0 else 1 for x in pxsize]

        new_imD = {"Dimensions": dims[:3],
            "NumberOfChannels": dims[3],
            "ChannelNames": chnames,
            "PixelPhysicalSize": pxsize,
            "PixelFormat": "uint8"}
        return new_imD


    def _init_leversc(self,strDB=None):
        leverpath = leversc._get_leverjs_path()
        if ( not self._run_leversc(leverpath,strDB) ):
            return False

        # Try to contact leversc after launch
        for _ in range(10):
            time.sleep(0.5)
            if ( self._check_leversc() ):
                return True

        print("Unable to contact Leversc app")
        return False


    def _run_leversc(self, leverpath,strDB):
        runargs = None
        if ( leverpath is None ):
            # Try to run installed leversc from path
            runargs = ["open","-a","leverjs.app","-n","--args"] if leversc._is_macos() else ["leverjs"]
        else:
            runargs = leversc._get_os_ljselectron_exec(leverpath)

        if ( runargs is None ):
            print("Unable to start Leversc app")
            return False

        if strDB is not None:
            strDB=os.path.abspath(strDB)
            runargs.append("--leverFile=%s" % strDB)
        port = self._base_port + self._figNumber
        runargs.append("--port=%s" % port)
        runargs.append("--title=figure %s" % self._figNumber)
        p = leversc._exec_bg_process(runargs)
        if ( p is None):
            return False
        return True


    @staticmethod
    def _get_os_ljselectron_exec(leverpath):
        runargs = None
        if ( leversc._is_windows() ):
            elec_path = os.path.join(leverpath,"node_modules","electron","dist","electron.exe")
            mainjs_path = os.path.join(leverpath,"elever","main.js")
            runargs = [elec_path, mainjs_path]
        elif ( leversc._is_linux() or leversc._is_macos() ):
            elec_path = os.path.join(leverpath,"node_modules",".bin","electron")
            mainjs_path = os.path.join(leverpath,"elever","main.js")
            runargs = [elec_path, mainjs_path]

        return runargs


    @staticmethod
    def _exec_bg_process(args):
        try:
            if ( leversc._is_windows() ):
                p = subprocess.Popen(args,
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            elif ( leversc._is_linux() or leversc._is_macos() ):
                p = subprocess.Popen(args,
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    start_new_session=True)
            else:
                return None
        except Exception as e:
            print("Unable to launch leversc: (%s)"%e)
            return None
        return p


    @staticmethod
    def _is_windows():
        return (sys.platform == "win32")

    @staticmethod
    def _is_linux():
        return (sys.platform == "linux" or sys.platform == "cygwin")

    @staticmethod
    def _is_macos():
        return (sys.platform == "darwin")


    @staticmethod
    def _get_leverjs_path():
        # Check if ljspath.py is on sys.path (e.g. PYTHONPATH)
        chk_ldr = pkgutil.find_loader("ljspath")
        if ( chk_ldr is None ):
            return None
        # Try to load the module
        ljs_m = chk_ldr.load_module("ljspath")
        if ( ljs_m is None ):
            return None
        return ljs_m.get_ljspath()

    from leversc._readImage import readImage
    from leversc._property import setProperty,getProperty
    @property
    def viewParams(self):
        return self.getProperty('viewParams')
    @viewParams.setter
    def viewParams(self,VP):
        self.setProperty('viewParams',VP)
    @property
    def renderParams(self):        
        return self.getProperty('renderParams')
    @renderParams.setter
    def renderParams(self,RP):
        self.setProperty('renderParams',RP)
    @property
    def uiParams(self):        
        return self.getProperty('uiParams')
    @uiParams.setter
    def uiParams(self,UIP):
        self.setProperty('uiParams',UIP)



