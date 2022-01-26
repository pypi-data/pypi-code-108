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

class __msview_class(object):
    "msview() task with local state for created viewer tool"

    def __init__( self ):
        pass

    def __call__(self, infile='',displaytype='raster',channel=0,zoom=1,outfile='',outscale=1.0,outdpi=300,outformat='jpg',outlandscape=False,gui=True):
        """ The msview will display measurement sets in raster form
        Many display and editing options are available.

        examples of usage:

        msview
        msview "mymeasurementset.ms"
        msview "myrestorefile.rstr"
        
        Executing the msview task will bring up a display panel
        window, which can be resized.  If no data file was specified,
        a Load Data window will also appear.  Click on the desired data
        file and choose the display type; the rendered data should appear
        on the display panel.

        A Data Display Options window will also appear.  It has drop-down
        subsections for related    options, most of which are self-explanatory.
      
        The state of the msview task -- loaded data and related display
        options -- can be saved in a 'restore' file for later use.
        You can provide the restore filename on the command line or
        select it from the Load Data window.

        See the cookbook for more details on using the msview task.
    
        Keyword arguments:
        infile -- Name of file to visualize
            default: ''
            example: infile='my.ms'
            If no infile is specified the Load Data window
            will appear for selecting data.
        displaytype -- (optional): method of rendering data
            visually (raster, contour, vector or marker).  
            You can also set this parameter to 'lel' and
            provide an lel expression for infile (advanced).
            default: 'raster'

        Note: there is no longer a filetype parameter; typing of
        data files is now done automatically.
                example:  msview infile='my.ms'
            obsolete: msview infile='my.ms', filetype='ms'


        """

        ##
        ## (1) save current *viewer*server* path
        ## (2) have viewer() task follow casapy/python's cwd
        try:
            old_path = viewertool.cwd(gui=gui)
        except:
            raise RuntimeError("msview() failed to get the current working directory")

        try:
            viewertool.cwd(os.path.abspath(os.curdir),gui)
        except:
            raise RuntimeError("msview() failed to change to the new working directory")
            
        data = None
        if type(infile) == str and len(infile) > 0 :
            info = viewertool.fileinfo(infile,gui);
            if info != 'ms' :
                if info == 'image' :
                    raise ValueError("msview() only displays images, try 'imview()'...")
                elif info == 'nonexistent' :
                    raise RuntimeError("ms (" + infile + ") could not be found...")
                else :
                    raise RuntimeError("unknow error...")

            panel = viewertool.panel("viewer",gui)
            if type(displaytype) == str:
                data = viewertool.load( infile, displaytype, panel=panel )
            else:
                data = viewertool.load( infile, panel=panel )

            if type(channel) == int and channel > 0 :
                viewertool.channel(channel,panel=panel)
            if type(zoom) == int and zoom != 1 :
                viewertool.zoom(zoom,panel=panel)
            if type(outfile) == str and len(outfile) > 0 :
                scale=1.0
                if type(outscale) == float :
                    scale=outscale
                dpi=300
                if type(outdpi) == int :
                    dpi=outdpi
                format="jpg"
                if type(outformat) == str :
                    format=outformat
                orientation="portrait"
                if type(outlandscape) == bool and outlandscape :
                    orientation="landscape"
                viewertool.output(outfile,scale=scale,dpi=dpi,format=format,orientation=orientation,panel=panel)
        else:
            panel = viewertool.panel("viewer", gui)
            if gui: viewertool.popup('open', panel=panel)

        ## (3) restore original path
        try:
            viewertool.cwd(old_path,gui)
        except:
            raise RuntimeError("msview() failed to restore the old working directory")

msview = __msview_class( )
