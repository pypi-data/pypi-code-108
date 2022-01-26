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
import sys
import os
import string
import time
from . import viewertool
from casatasks import casalog

###
### if numpy is not available, make float64 and ndarray redundant checks...
###
try:
    from numpy import float64 as float64
    from numpy import ndarray as ndarray
except:
    float64 = float
    ndarray = list

class __imview_class(object):
    "imview() task with local state for created viewer tool"

    def __init__( self ):
        self.__dirstack = [ ]
        self.__colorwedge_queue = [ ]

    def __call__( self, raster={ }, contour={ }, zoom=1, axes={ }, out='' ):
        """ Old parameters:
               infile=None,displaytype=None,channel=None,zoom=None,outfile=None,
               outscale=None,outdpi=None,outformat=None,outlandscape=None,gui=None
        The imview task will display images in raster, contour, vector or
        marker form.  Images can be blinked, and movies are available
        for spectral-line image cubes.  For measurement sets, many
        display and editing options are available.

        examples of usage:

        imview
        imview "myimage.im"
        imview "myrestorefile.rstr"
        
        imview "myimage.im", "contour"

        imview "'myimage1.im' - 2 * 'myimage2.im'", "lel"
    
        Executing imview( ) will bring up a display panel
        window, which can be resized.  If no data file was specified,
        a Load Data window will also appear.  Click on the desired data
        file and choose the display type; the rendered data should appear
        on the display panel.

        A Data Display Options window will also appear.  It has drop-down
        subsections for related options, most of which are self-explanatory.
      
        The state of the imview task -- loaded data and related display
        options -- can be saved in a 'restore' file for later use.
        You can provide the restore filename on the command line or
        select it from the Load Data window.

        See the cookbook for more details on using the imview task.
    
        Keyword arguments:
        infile -- Name of file to visualize
            default: ''
            example: infile='ngc5921.image'
            If no infile is specified the Load Data window
            will appear for selecting data.
        displaytype -- (optional): method of rendering data
            visually (raster, contour, vector or marker).  
            You can also set this parameter to 'lel' and
            provide an lel expression for infile (advanced).
            default: 'raster'
            example: displaytype='contour'

        Note: the filetype parameter is optional; typing of
                data files is now inferred.
                example:  imview infile='my.im'
            implies:  imview infile='my.im', filetype='raster'
        the filetype is still used to load contours, etc.


        """
        casalog.origin('imview')
        
        has_out = False
        if (type(out) == str and len(out) != 0) or \
               (type(out) == dict and len(out) != 0) :
            gui = False
            has_out = True
            # gui = False is only allowed for Linux platforms
            if sys.platform != 'linux':
                # has_out will be used later to drive output generation independent of gui value
                gui = True
            (out_file, out_format, out_scale, out_dpi, out_orientation) = self.__extract_outputinfo( out )
        else:
            gui = True

        self.__pushd( gui, os.path.abspath(os.curdir) )

        if (raster is None or len(raster) == 0) and \
           (contour is None or len(contour) == 0) :
            panel = self.__panel(gui)
        else:
            panel = self.__load_files( "raster", gui, None, raster )
            panel = self.__load_files( "contour", gui, panel, contour )
            
        self.__set_axes( panel, axes )
        self.__zoom( panel, zoom )
        self.__process_colorwedges( panel )

        if has_out:
            viewertool.output(out_file,scale=out_scale,dpi=out_dpi,format=out_format,orientation=out_orientation,panel=panel)
            viewertool.close(panel)

        self.__popd( )

    def __panel( self, gui ):
        panel = viewertool.panel("viewer",gui)
        return panel

    def __load_raster( self, gui, panel, raster ):
        ## here we can assume we have a dictionary
        ## that specifies what needs to be done...
        data = None
        if not 'file' in raster:
            return panel

        if  type(raster['file']) != str or not os.path.exists(raster['file']) or \
               viewertool.fileinfo(raster['file'],gui) != 'image':
            casalog.post( str(raster['file']) + " does not exist or is not an image", 'SEVERE')
            raise RuntimeError(raster['file'] + " does not exist or is not an image")

        if panel is None:
            panel = self.__panel(gui)
        
        scaling = 0.0
        if 'scaling' in raster:
            scaling = self.__checknumeric(raster['scaling'], float, "raster scaling")

            
        data = viewertool.load( raster['file'], 'raster', panel=panel, scaling=scaling )
        
        if 'range' in raster:
            viewertool.datarange( self.__checknumeric(raster['range'], float, "data range", array_size=2), data=data )

        if 'colormap' in raster:
            if type(raster['colormap']) == str:
                viewertool.colormap( raster['colormap'], data )
            else:
                casalog.post( "raster colormap must be a string", 'SEVERE')
                raise RuntimeError("raster colormap must be a string")

        if 'colorwedge' in raster:
            if type(raster['colorwedge']) == bool:
                self.__colorwedge_queue.append( (data,raster['colorwedge']) )
            else:
                casalog.post( "colorwedge must be a boolean", 'SEVERE')
                raise RuntimeError("colorwedge must be a boolean")

        return panel

    def __process_colorwedges( self, panel ):
        self.__colorwedge_queue.reverse( )
        while len(self.__colorwedge_queue) > 0:
            element = self.__colorwedge_queue.pop( )
            viewertool.colorwedge( element[1], element[0] )

    def __load_contour( self, gui, panel, contour ):
        ## here we can assume we have a dictionary
        ## that specifies what needs to be done...
        data = None
        if not 'file' in contour:
            return panel

        if type(contour['file']) != str or not os.path.exists(contour['file']) or \
               viewertool.fileinfo(contour['file'],gui) != 'image':
            casalog.post( str(contour['file']) + " does not exist or is not an image", 'SEVERE')
            raise RuntimeError(contour['file'] + " does not exist or is not an image")

        if panel is None:
            panel = self.__panel(gui)

        data = viewertool.load( contour['file'], 'contour', panel=panel )

        if 'levels' in contour:
            viewertool.contourlevels( self.__checknumeric(contour['levels'], float, "contour levels", array_size=0), data=data )
        if 'unit' in contour:
            viewertool.contourlevels( unitlevel=self.__checknumeric(contour['unit'], float, "contour unitlevel"), data=data )
        if 'base' in contour:
            viewertool.contourlevels( baselevel=self.__checknumeric(contour['base'], float, "contour baselevel"), data=data )

        try:
            if 'thickness' in contour:
                viewertool.contourthickness( thickness=self.__checknumeric(contour['thickness'], float, "contour thickness"), data=data )
            if 'color' in contour:
                viewertool.contourcolor( contour['color'], data=data )
        except:
            print("viewertool error: %s" % sys.exc_info()[1])

        return panel

    def __set_axes( self, panel, axes ):
        x=''
        y=''
        z=''
        invoke = False
        if type(axes) == list and len(axes) == 3 and \
           all( map( lambda x: type(x) == str, axes ) ) :
            x = axes[0]
            y = axes[1]
            z = axes[2]
            invoke = True
        elif type(axes) == dict :
            if 'x' in axes:
                if type(axes['x']) != str:
                    casalog.post( "dimensions of axes must be strings (x is not)", 'SEVERE')
                    raise RuntimeError("dimensions of axes must be strings (x is not)")
                x = axes['x']
                invoke = True
            if 'y' in axes:
                if type(axes['y']) != str:
                    casalog.post( "dimensions of axes must be strings (y is not)", 'SEVERE')
                    raise RuntimeError("dimensions of axes must be strings (y is not)")
                y = axes['y']
                invoke = True
            if 'z' in axes:
                if type(axes['z']) != str:
                    casalog.post( "dimensions of axes must be strings (z is not)", 'SEVERE')
                    raise RuntimeError("dimensions of axes must be strings (z is not)")
                z = axes['z']
                invoke = True
        else :
            casalog.post( "'axes' must either be a string list of 3 dimensions or a dictionary", 'SEVERE')
            raise RuntimeError("'axes' must either be a string list of 3 dimensions or a dictionary")

        result = False
        if invoke:
            viewertool.axes( x, y, z, panel=panel )
            result = True

        return result


    def __zoom( self, panel, zoom ) :

        channel = -1
        if type(zoom) == dict and 'channel' in zoom:
            channel = self.__checknumeric(zoom['channel'], int, "channel")

        if type(zoom) == int :
            viewertool.zoom(level=zoom,panel=panel)
        elif type(zoom) == str and os.path.isfile( zoom ):
            viewertool.zoom(region=zoom,panel=panel)
        elif type(zoom) == dict and 'blc' in zoom and 'trc' in zoom:
            blc = zoom['blc']
            trc = zoom['trc']
            if type(blc) == list and type(trc) == list:
                blc = self.__checknumeric( blc, float, "zoom blc", array_size=2 )
                trc = self.__checknumeric( trc, float, "zoom trc", array_size=2 )

                coord = "pixel"
                if 'coordinates' in zoom:
                    if 'coord' in zoom:
                        casalog.post( "cannot specify both 'coord' and 'coordinates' for zoom", 'SEVERE')
                        raise RuntimeError("cannot specify both 'coord' and 'coordinates' for zoom")
                    if type(zoom['coordinates']) != str:
                        casalog.post( "zoom coordinates must be a string", 'SEVERE')
                        raise RuntimeError("zoom coordinates must be a string")
                    coord = zoom['coordinates']
                    if coord != 'world' and coord != 'pixel' :
                        casalog.post( "zoom coordinates must be either 'world' or 'pixel'", 'SEVERE')
                        raise RuntimeError("zoom coordinates must be either 'world' or 'pixel'")
                elif 'coord' in zoom:
                    if type(zoom['coord']) != str:
                        casalog.post( "zoom coord must be a string", 'SEVERE')
                        raise RuntimeError("zoom coord must be a string")
                    coord = zoom['coord']
                    if coord != 'world' and coord != 'pixel' :
                        casalog.post( "zoom coord must be either 'world' or 'pixel'", 'SEVERE')
                        raise RuntimeError("zoom coord must be either 'world' or 'pixel'")
                if channel >= 0:
                    viewertool.channel( channel, panel=panel )
                viewertool.zoom(blc=blc,trc=trc, coordinates=coord, panel=panel)
            elif type(blc) == dict and type(trc) == dict and \
                 '*1' in blc.has_key(  ) and '*1' in trc:
                if channel >= 0:
                    viewertool.channel( channel, panel=panel )
                viewertool.zoom(region=zoom,panel=panel)
            else:
                casalog.post( "zoom blc & trc must be either lists or dictionaries", 'SEVERE')
                raise RuntimeError("zoom blc & trc must be either lists or dictionaries")

        elif type(zoom) == dict and 'regions' in zoom:
            if channel >= 0:
                viewertool.channel( channel, panel=panel )
            viewertool.zoom(region=zoom,panel=panel)
        elif type(zoom) == dict and 'file' in zoom and type(zoom['file']) == str and os.path.isfile( zoom['file'] ):
            if channel >= 0:
                viewertool.channel( channel, panel=panel )
            viewertool.zoom(region=zoom['file'],panel=panel)
        else:
            if channel < 0:
                casalog.post( "invalid zoom parameters", 'SEVERE')
                raise RuntimeError("invalid zoom parameters")
            else:
                viewertool.channel( channel, panel=panel )
        viewertool.show(panel=panel)

    def __load_files( self, filetype, gui, panel, files ):

        if filetype != "raster" and filetype != "contour":
            casalog.post( "internal error __load_files( )...", 'SEVERE')
            raise RuntimeError("internal error __load_files( )...")

        if type(files) == str:
            panel = self.__load_raster( gui, panel, { 'file': files } ) if filetype == 'raster' else \
                        self.__load_contour( gui, panel, { 'file': files } )
        elif type(files) == dict:
            panel = self.__load_raster( gui, panel, files ) if filetype == 'raster' else \
                        self.__load_contour( gui, panel, files )
        elif type(files) == list:
            if all(map( lambda x: type(x) == dict, files )):
                for f in files:
                    panel = self.__load_raster( gui, panel, f ) if filetype == 'raster' else \
                                self.__load_contour( gui, panel, f )
            elif all(map( lambda x: type(x) == str, files )):
                for f in files:
                    panel = self.__load_raster( gui, panel, { 'file': f } ) if filetype == 'raster' else \
                                self.__load_contour( gui, panel, { 'file': f } )
            else:
                casalog.post( "multiple " + str(filetype) + " specifications must be either all dictionaries or all strings", 'SEVERE')
                raise RuntimeError("multiple " + filetype + " specifications must be either all dictionaries or all strings")
        else:
            casalog.post( filetype + "s can be a single file path (string), a single specification (dictionary), or a list containing all strings or all dictionaries", 'SEVERE')
            raise RuntimeError(filetype + "s can be a single file path (string), a single specification (dictionary), or a list containing all strings or all dictionaries")
        return panel


    def __extract_outputinfo( self, out ):
        output_file=None
        output_format=None
        output_scale=1.0
        output_dpi=300
        output_orientation="portrait"
        
        if type(out) == str:
            output_format = self.__check_filename(out)
            output_file = out

        elif type(out) == dict:
            if 'file' in out:
                if type(out['file']) != str:
                    casalog.post( "output filename must be a string", 'SEVERE')
                    raise RuntimeError("output filename must be a string")
                if 'format' in out:
                    if type(out['format']) != str:
                        casalog.post( "output format must be a string", 'SEVERE')
                        raise RuntimeError("output format must be a string")
                    output_format = self.__check_fileformat( out['format'] )
                    self.__check_filename( out['file'], False )
                else:
                    output_format = self.__check_filename( out['file'] )

                output_file = out['file']

            else:
                casalog.post( "an output dictionary must include a 'file' field", 'SEVERE')
                raise RuntimeError("an output dictionary must include a 'file' field")

            if 'scale' in out:
                output_scale = self.__checknumeric(out['scale'], float, "output scale")

            if 'dpi' in out:
                output_dpi = self.__checknumeric(out['dpi'], int, "output dpi")
                output_dpi = int(out['dpi'])

            if 'orientation' in out:
                if 'orient' in out:
                    casalog.post( "output dictionary cannot have both 'orient' and 'orientation' fields", 'SEVERE')
                    raise RuntimeError("output dictionary cannot have both 'orient' and 'orientation' fields")
                if type(out['orientation']) != str:
                    casalog.post( "output orientation must be a string", 'SEVERE')
                    raise RuntimeError("output orientation must be a string")
                if out['orientation'] != 'portrait' and out['orientation'] != 'landscape':
                    casalog.post( "output orientation must be either 'portrait' or 'landscape'", 'SEVERE')
                    raise RuntimeError("output orientation must be either 'portrait' or 'landscape'")
                output_orientation = out['orientation']

            if 'orient' in out:
                if type(out['orient']) != str:
                    casalog.post( "output orient field must be a string", 'SEVERE')
                    raise RuntimeError("output orient field must be a string")
                if out['orient'] != 'portrait' and out['orient'] != 'landscape':
                    casalog.post( "output orient field must be either 'portrait' or 'landscape'", 'SEVERE')
                    raise RuntimeError("output orient field must be either 'portrait' or 'landscape'")
                output_orientation = out['orient']

        return (output_file, output_format, output_scale, output_dpi, output_orientation)

    def __checknumeric( self, value, otype, error_string, array_size=None ):
        if array_size is not None:
            if type(array_size) != int:
                casalog.post( "internal error: array_size is expected to be of type int", 'SEVERE')
                raise RuntimeError("internal error: array_size is expected to be of type int")
            if type(value) != list and not isinstance(value,ndarray):
                casalog.post( error_string + " must be a list", 'SEVERE')
                raise RuntimeError(error_string + " must be a list")
            if array_size > 0 and len(value) != array_size:
                numbers = { '1': 'one', '2': 'two', '3': 'three' }
                casalog.post( error_string + " can only be a " + numbers[str(array_size)] + " element numeric list", 'SEVERE')
                raise RuntimeError(error_string + " can only be a " + numbers[str(array_size)] + " element numeric list")
            if not all(map( lambda x: type(x) == int or type(x) == float or isinstance(x,float64), value )):
                casalog.post( error_string + " must be a numeric list", 'SEVERE')
                raise RuntimeError(error_string + " must be a numeric list")
            return list(map( lambda x: otype(x), value ))
                    
        if type(value) != int and type(value) != float:
            casalog.post( error_string + " must be numeric", 'SEVERE')
            raise RuntimeError(error_string + " must be numeric")

        return otype(value)

    def __check_fileformat( self, ext ):
        supported_files = [ 'jpg', 'pdf', 'eps', 'ps', 'png', 'xbm', 'xpm', 'ppm' ]
        if supported_files.count(ext.lower( )) == 0:
            casalog.post( "output format '" + str(ext) + "' not supported; supported types are: " + str(supported_files), 'SEVERE')
            raise RuntimeError("output format '" + str(ext) + "' not supported; supported types are: " + str(supported_files))
        return ext.lower( )


    def __check_filename( self, out, check_extension = True ):
        dir = os.path.dirname(out)
        if len(dir) > 0 and not os.path.isdir(dir):
            casalog.post( "output directory (" + str(dir) + ") does not exist", 'SEVERE')
            raise RuntimeError("output directory (" + str(dir) + ") does not exist")
        file = os.path.basename(out)
        if len(file) == 0:
            casalog.post( "could not find a valid file name in '" + str(out) + "'", 'SEVERE')
            raise RuntimeError("could not find a valid file name in '" + str(out) + "'")
        (base,ext) = os.path.splitext(file)
        if len(ext) == 0:
            casalog.post( "could not infer the ouput type from file name '" + str(file) + "'", 'SEVERE')
            raise RuntimeError("could not infer the ouput type from file name '" + str(file) + "'")
        return self.__check_fileformat(ext[1:]) if check_extension else ''

    def __pushd( self, gui, newdir ):
        try:
            old_path = viewertool.cwd( gui=gui )
        except:
            casalog.post( "imview() failed to get the current working directory [" + str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "]", 'SEVERE')
            raise RuntimeError("imview() failed to get the current working directory [" + str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "]")

        self.__dirstack.append((gui,old_path))
        try:
            viewertool.cwd(newdir,gui)
        except:
            casalog.post( "imview() failed to change to the new working directory (" + os.path.abspath(os.curdir) + ") [" + str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "]", 'SEVERE')
            raise RuntimeError("imview() failed to change to the new working directory (" + os.path.abspath(os.curdir) + ") [" + str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "]")


    def __popd( self ):
        try:
            gui, path = self.__dirstack.pop( )
            viewertool.cwd(path,gui)
        except:
            casalog.post( "imview() failed to restore the old working directory (" + old_path + ") [" + str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "]", 'SEVERE')
            raise RuntimeError("imview() failed to restore the old working directory (" + old_path + ") [" + str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "]")


imview = __imview_class( )
