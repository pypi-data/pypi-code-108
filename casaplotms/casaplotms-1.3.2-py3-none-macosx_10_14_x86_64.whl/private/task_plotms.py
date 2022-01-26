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
import os
import sys
import time
import traceback
from casatasks import casalog
from casatools import ctsys
from . import plotmstool as pm


def plotms(vis="",
           gridrows=1, gridcols=1,
           rowindex=0,colindex=0,
           plotindex=0,
           xaxis="", xdatacolumn="", xframe="", xinterp="",
           yaxis="", ydatacolumn="", yframe="", yinterp="", yaxislocation="",
           selectdata=True, field="", spw="",
           timerange="", uvrange="", antenna="", scan="",
           correlation="", array="", observation="", 
           intent="", feed="", msselect="",
           averagedata=True,
           avgchannel="", avgtime="", avgscan=False, avgfield=False,
           avgbaseline=False, avgantenna=False, avgspw=False, scalar=False,
           transform=True,
           freqframe="",restfreq="",veldef="RADIO",shift=[0.0,0.0],
           extendflag=False,
           extcorr=False, extchannel=False,
           iteraxis="",xselfscale=False,yselfscale=False,
           xsharedaxis=False, ysharedaxis=False,
           customsymbol=False, symbolshape="autoscaling", symbolsize=2,
           symbolcolor="0000ff", symbolfill="fill", symboloutline=False,
           coloraxis="",
           customflaggedsymbol=False, flaggedsymbolshape="circle",
           flaggedsymbolsize=2, flaggedsymbolcolor="ff0000",
           flaggedsymbolfill="fill", flaggedsymboloutline=False,
           xconnector="", timeconnector=False,
           plotrange=[ ],
           title="", titlefont=0, 
           xlabel="", xaxisfont=0, ylabel="", yaxisfont=0,
           showmajorgrid=False, majorwidth=1, majorstyle="",  majorcolor="B0B0B0",    
           showminorgrid=False, minorwidth=1, minorstyle="",  minorcolor="D0D0D0", 
           showlegend=False, legendposition="",   
           plotfile="", expformat="", verbose=True, exprange="",
           highres=False, dpi=-1, width=-1, height=-1, overwrite=False,
           showgui=True, clearplots=True,
           callib="", headeritems="", showatm=False, showtsky=False, showimage=False):
# we'll add these later
#           extspw=None, extantenna=None,
#           exttime=None, extscans=None, extfield=None,

    """
    
            Task for plotting and interacting with visibility data.  A variety
        of axes choices (including data column) along with MS selection and
        averaging options are provided for data selection.  Flag extension
        parameters are also available for flagging operations in the plotter.
        
            All of the provided parameters can also be set using the GUI once
        the application has been launched.  Additional and more specific
        operations are available through the GUI and/or through the plotms
        tool (pm).
        

    Keyword arguments:
    vis -- input visibility dataset
           default: ''
    
    gridrows -- Number of subplot rows.
                    default: 1
    gridcols -- Number of subplot columns.
                    default: 1 
    rowindex -- Row location of the subplot (0-based).
                    default: 0
    colindex -- Column location of the subplot (0-based).
                    default: 0          
    plotindex -- Index to address a subplot (0-based).
                    default: 0            
    xaxis, yaxis -- what to plot on the two axes
                    default: '' (uses PlotMS defaults/current set).
        &gt;&gt;&gt; xaxis, yaxis expandable parameters
        xdatacolumn, 
        ydatacolumn -- which data column to use for data axes
                       default: '' (uses PlotMS default/current set).
        xframe,
        yframe      -- which coordinates frame to use for ant-ra,ant-dec axes
                       default: '' (uses PlotMS default/current set).
        xinterp,
        yinterp     -- which interpolation method to use for ant-ra,ant-dec axes
                       default: '' (uses PlotMS default/current set).
        yaxislocation -- whether the data should be plotted using the left or right y-axis
                       default: '' (uses PlotMS default).
    iteraxis -- what axis to iterate on when doing iteration plots
                default: ''
              &gt;&gt;&gt; xsharedaxis, ysharedaxis, xselfscale, yselfscale expandable parameters 
        xselfscale -- If true, iterated plots should share a common x-axis label per column.
                       default: False.
        yselfscale -- If true, iterated plots should share a common y-axis label per row.
                       default: False.
        xsharedaxis -- use a common x-axis for vertically aligned plots (must also set xselfscale=True)
                        default: False.
        ysharedaxis -- use a common y-axis for horizontally aligned plots (must also set yselfscale=True)
                        default: False.
    selectdata -- data selection parameters flag
                  (see help par.selectdata for more detailed information)
                  default: False
      &gt;&gt;&gt; selectdata expandable parameters
        field -- select using field ID(s) or field name(s)
                 default: '' (all).
        spw -- select using spectral window/channels
               default: '' (all)
        timerange -- select using time range
                     default: '' (all).
        uvrange -- select using uvrange
                   default: '' (all).
        antenna -- select using antenna/baseline
                   default: '' (all).
        scan -- select using scan number
                default: '' (all).
        correlation -- select using correlations
                       default: '' (all).
        array -- select using (sub)-array range
                 default: '' (all).
        observation -- select by observation ID(s).
                 default: '' (all).
        intent -- select observing intent  
                  default: ''  (no selection by intent)  
                  intent='*BANDPASS*'  (selects data labelled with  
                                        BANDPASS intent)
        feed   -- select feed ID
                  default: '' (all)
                  feed='1~2'
        msselect -- TaQL selection expression
                    default: '' (all).
    
    averagedata -- data averaging parameters flag
                   default: False.
      &gt;&gt;&gt; averagedata expandable parameters
        avgchannel -- average over channel?  either blank for none, or a value
                      in channels.
                      default: '' (none).
        avgtime -- average over time?  either blank for none, or a value in
                   seconds.
                   default: '' (none).
        avgscan -- average over scans?  only valid if time averaging is turned
                   on.
                   default: False.
        avgfield -- average over fields?  only valid if time averaging is
                    turned on.
                    default: False.
        avgbaseline -- average over all baselines?  mutually exclusive with
                       avgantenna.
                       default: False.
        avgantenna -- average by per-antenna?  mutually exclusive with
                      avgbaseline.
                      default: False.
        avgspw -- average over all spectral windows?
                  default: False.
    
    extendflag -- have flagging extend to other data points?
                  default: False.
      &gt;&gt;&gt; extendflag expandable parameters
        extcorr -- extend flags based on correlation?  blank = none.
                          default: ''.
        extchannel -- extend flags based on channel?
                      default: False.
        extspw -- extend flags based on spw?
                  default: False.
        extantenna -- extend flags based on antenna?  should be either blank,
                      'all' for all baselines, or an antenna-based value.
                      default: ''.
        exttime -- extend flags based on time (within scans)?
                   default: False.
        extscans -- extend flags based on scans?  only valid if time extension
                    is turned on.
                    default: False.
        extfield -- extend flags based on field?  only valid if time extension
                    is turned on.
                    default: False.

    coloraxis -- which axis to use for colorizing
                     default: ''  (ignored - same as colorizing off)              
    
    title  -- title along top of plot (called "canvas" in some places)
    titlefont -- plot title font size
                 default: 0 (autosize depending on grid)
    exprange -- Export all iteration plots ('all') or only the current one.
                    default: '' (only export the current iteration plot)
    xlabel, ylabel -- text to label horiz. and vert. axes, with formatting (%% and so on)
    xaxisfont, yaxisfont -- int for axis font size
    
    showlegend -- show a legend on the plot
                    default: False
    legendposition -- position for the legend.  Legends can be interior or exterior to the plot
                    Interior legends can be located in the upper right, lower right, upper left, or lower left.
                    Exterior legends can be located on the right, left, top, or bottom.
                    default: 'upperright'
    showgui -- Whether or not to display the plotting GUI
                    default: True; example showgui=False
    clearplots -- clear existing plots so that the new ones coming in can replace them.                 
    callib -- calibration library string, list of strings, or filename for on-the-fly calibration
    headeritems -- string of comma-separated page header items keywords
    showatm -- show atmospheric transmission curve
    showtsky -- show sky temperature curve
    showimage -- show image sideband curve

    """
    # Check if DISPLAY environment variable is set.
    if os.getenv('DISPLAY') == None:
        raise RuntimeError('ERROR: DISPLAY environment variable is not set! Cannot run plotms.')

    # check arguments
    # check plotfile for export
    if plotfile:
        if not vis:
            raise RuntimeError("vis not set, cannot export empty plot")
        if not os.path.dirname(plotfile):
            plotfile = os.path.join(os.getcwd(), plotfile)
        if (os.path.exists(plotfile) and not overwrite):
            raise RuntimeError("plot file " + plotfile + " exists and overwrite is false, cannot write the file")

    # Define axis synonyms
    # format is:  synonym['new_term'] = 'existing_term'
    # existing_term in PlotMSConstants.h
    # CAS-8532: match capitalization in axis names in GUI
    synonyms = {}
    synonyms['Scan'] = 'scan'
    synonyms['Field'] = 'field'
    synonyms['Time'] = 'time'
    synonyms['timeinterval'] = synonyms['timeint'] = synonyms['time_interval'] = synonyms['Interval'] = 'interval'
    synonyms['Spw'] = 'spw'
    synonyms['chan'] = synonyms['Channel'] = 'channel'
    synonyms['freq'] = synonyms['Frequency'] = 'frequency'
    synonyms['vel'] = synonyms['Velocity'] = 'velocity'
    synonyms['correlation'] = synonyms['Corr'] = 'corr'
    synonyms['ant1'] = synonyms['Antenna1'] = 'antenna1'
    synonyms['ant2'] = synonyms['Antenna2'] = 'antenna2'
    synonyms['Baseline'] = 'baseline'
    synonyms['Row'] = 'row'
    synonyms['Observation'] = 'observation'
    synonyms['Intent'] = 'intent'
    synonyms['Feed1'] = 'feed1'
    synonyms['Feed2'] = 'feed2'
    synonyms['amplitude'] = synonyms['Amp'] = 'amp'
    synonyms['Phase'] = 'phase'
    synonyms['Real'] = 'real'
    synonyms['imaginary'] = synonyms['Imag'] = 'imag'
    synonyms['weight'] = synonyms['Wt'] = synonyms['Weight'] = 'wt'
    synonyms['wtamp'] = synonyms['Wt*Amp'] = 'wtamp'
    synonyms['weightspectrum'] = synonyms['WtSp'] = synonyms['WeightSpectrum'] = 'wtsp'
    synonyms['Sigma'] = 'sigma'
    synonyms['sigmaspectrum'] = synonyms['SigmaSpectrum'] = synonyms['SigmaSp'] = 'sigmasp'
    synonyms['Flag'] = 'flag'
    synonyms['FlagRow'] = 'flagrow'
    synonyms['UVdist'] = 'uvdist'
    synonyms['uvdistl'] = synonyms['uvdist_l']=synonyms['UVwave'] = 'uvwave'
    synonyms['U'] = 'u'
    synonyms['V'] = 'v'
    synonyms['W'] = 'w'
    synonyms['Uwave'] = 'uwave'
    synonyms['Vwave'] = 'vwave'
    synonyms['Wwave'] = 'wwave'
    synonyms['Azimuth'] = 'azimuth'
    synonyms['Elevation'] = 'elevation'
    synonyms['hourang'] = synonyms['HourAngle'] = 'hourangle'
    synonyms['parang'] = synonyms['parallacticangle'] = synonyms['ParAngle'] = 'parangle'
    synonyms['ant'] = synonyms['Antenna'] = 'antenna'
    synonyms['Ant-Azimuth'] = 'ant-azimuth'
    synonyms['Ant-Elevation'] = 'ant-elevation'
    synonyms['Ant-Ra'] = synonyms['Ant-RA'] = 'ant-ra'
    synonyms['Ant-Dec'] = synonyms['Ant-DEC'] = 'ant-dec'
    synonyms['ant-parallacticangle']=synonyms['ant-parang'] = synonyms['Ant-ParAngle'] = 'ant-parangle'
    synonyms['gamp']=synonyms['gainamp']=synonyms['GainAmp']='Gain Amp'
    synonyms['gphase']=synonyms['gainphase']=synonyms['GainPhase']='Gain Phase'
    synonyms['greal']=synonyms['gainreal']=synonyms['GainReal']='Gain Real'
    synonyms['gimag']=synonyms['gainimag']=synonyms['GainImag']='Gain Imag'
    synonyms['del']=synonyms['delay']=synonyms['Delay']='delay'
    synonyms['rate']=synonyms['delayrate']=synonyms['DelayRate']='Delay Rate'
    synonyms['disp']=synonyms['dispdelay']=synonyms['DispDelay']='Disp Delay'
    synonyms['swp']=synonyms['swpower']=synonyms['switchedpower']=synonyms['SwPower']=synonyms['spgain']='swpower'
    synonyms['tsys']=synonyms['Tsys']=synonyms['TSYS']='tsys'
    synonyms['opac']=synonyms['opacity']=synonyms['Opac']='opac'
    synonyms['snr']='SNR'
    synonyms['tec']='TEC'
    synonyms['antpos']='Antenna Positions'
    synonyms['radialvelocity']= synonyms['Radial Velocity'] = 'Radial Velocity'
    synonyms['rho']=synonyms['Distance']='Distance (rho)'
    # data columns: unspecified residuals default to vector
    synonyms['residual']=synonyms['corrected-model']='corrected-model_vector'
    synonyms['data-model']='data-model_vector'
    synonyms['corrected/model']='corrected/model_vector'
    synonyms['data/model']='data/model_vector'
    #synonyms['azelgeo']='AzEl'

    # Do preliminary checks on argument values
    # Set synonyms to existing_terms
    if(xaxis in synonyms):
        xaxis = synonyms[xaxis]
    if isinstance(yaxis, str):
        if yaxis in synonyms:
            yaxis = synonyms[yaxis]
    elif isinstance(yaxis, list):
        for index,axis in enumerate(yaxis):
            if axis in synonyms:
                yaxis[index] = synonyms[axis]

    if isinstance(coloraxis, str):
        if coloraxis in synonyms:
            coloraxis = synonyms[coloraxis]

    if(xdatacolumn in synonyms):
        xdatacolumn = synonyms[xdatacolumn]
    if isinstance(ydatacolumn, str):
        if ydatacolumn in synonyms:
            ydatacolumn = synonyms[ydatacolumn]
    elif isinstance(ydatacolumn, list):
        for index,col in enumerate(ydatacolumn):
            if col in synonyms:
                ydatacolumn[index] = synonyms[col]

    if isinstance(xframe, str):
        if xframe in synonyms:
            xframe = synonyms[xframe]
    elif isinstance(xframe, list):
        for index,frame in enumerate(xframe):
            if frame in synonyms:
                xframe[index] = synonyms[frame]

    if isinstance(yframe, str):
        if yframe in synonyms:
            yframe = synonyms[yframe]
    elif isinstance(yframe, list):
        for index,frame in enumerate(yframe):
            if frame in synonyms:
                yframe[index] = synonyms[frame]

    # check variant parameter values; synonyms already converted
    if yaxis:
        valid_axes = ['scan', 'field', 'time', 'interval', 'spw', 'channel',
            'frequency', 'velocity', 'corr', 'antenna1', 'antenna2', 'baseline',
            'row', 'observation', 'intent', 'feed1', 'feed2',
            'amp', 'phase', 'real', 'imag', 'wt', 'wt*amp', 'wtsp',
            'sigma', 'sigmasp', 'flag', 'flagrow', 'uvdist',
            'uvwave', 'u', 'v', 'w', 'uwave', 'vwave', 'wwave',
            'azimuth', 'elevation', 'hourangle', 'parangle', 'antenna',
            'ant-azimuth', 'ant-elevation', 'ant-ra', 'ant-dec',
            'ant-parangle', 'Gain Amp', 'Gain Phase', 'Gain Real',
            'Gain Imag', 'delay', 'Delay Rate', 'Disp Delay', 'swpower', 'tsys', 'opac', 'SNR',
            'TEC', 'Antenna Positions', 'Radial Velocity', 'Distance (rho)']
        checkVariantString('yaxis', yaxis, valid_axes)
    if ydatacolumn:
        valid_columns = ["data", "corrected", "model", "float",
            "corrected-model_vector", "corrected-model_scalar",
            "data-model_vector", "data-model_scalar",
            "corrected/model_vector", "corrected/model_scalar",
            "data/model_vector", "data/model_scalar"]
        checkVariantString('ydatacolumn', ydatacolumn, valid_columns)
    if yframe:
        valid_frames = ['icrs', 'j2000', 'b1950', 'galactic', 'azelgeo']
        checkVariantString('yframe', yframe, valid_frames)
    if yinterp:
        valid_interps = ['nearest', 'cubic spline', 'spline']
        checkVariantString('yinterp', yinterp, valid_interps)
    if yaxislocation:
        valid_locations = ['left', 'right']
        checkVariantString('yaxislocation', yaxislocation, valid_locations)
    # custom symbols
    valid_shapes = ['nosymbol', 'autoscaling', 'circle', 'square', 'diamond', 'pixel']
    valid_fill = ['fill', 'mesh1', 'mesh2', 'mesh3', 'nofill']
    checkVariantBool('customsymbol', customsymbol)
    if customsymbol:
        checkVariantInt('symbolsize', symbolsize)
        if symbolshape:
            checkVariantString('symbolshape', symbolshape, valid_shapes)
        if symbolcolor:
            checkVariantString('symbolcolor', symbolcolor, [])
        if symbolfill:
            checkVariantString('symbolfill', symbolfill, valid_fill)
    checkVariantBool('customflaggedsymbol', customflaggedsymbol)
    if customflaggedsymbol:
        checkVariantInt('flaggedsymbolsize', flaggedsymbolsize)
        if flaggedsymbolshape:
            checkVariantString('flaggedsymbolshape', flaggedsymbolshape, valid_shapes)
        if flaggedsymbolcolor:
            checkVariantString('falggedsymbolcolor', flaggedsymbolcolor, [])
        if flaggedsymbolfill:
            checkVariantString('flaggedsymbolfill', flaggedsymbolfill, valid_fill)

    # check vis exists
    vis = vis.strip()
    if len(vis) > 0:
        vis = os.path.abspath(vis)
        if not os.path.exists(vis):
            raise RuntimeError('\n'.join(['Input file not found:',vis]))

    # check plotindex
    if plotindex < 0:
        raise ValueError("a negative plotindex is not valid.")
    if clearplots and plotindex > 0:
        raise ValueError("a nonzero plotindex is not valid when clearing plots.")
    else:
        numplots = pm.getNumPlots()
        if plotindex > numplots:
           casalog.post("Invalid plot index, setting to " + str(numplots), "WARN")
           plotindex = numplots

    # Determine whether this is going to be a scripting client or
    # a full GUI supporting user interaction.  This must be done
    # before any other properties are set because it affects the
    # constructor of plotms.
    if ctsys.getnogui():
        showgui = False
    pm.setShowGui( showgui )

    if clearplots:
        # Clear any existing plots unless still drawing last one
        if pm.isDrawing():
            raise RuntimeError("plotms is running in GUI mode and cannot be run again until the current drawing completes.")
        pm.clearPlots()

    # set grid
    pm.setGridSize( gridrows, gridcols )

    # set vis filename
    pm.setPlotMSFilename(vis, False, plotindex )

    # set yaxis defaults as needed
    if isinstance(yaxis, str):
        if yaxis == 'ant-ra' or yaxis == 'ant-dec':
            # Handle empty lists as empty strings
            if isinstance(yinterp, list) and not yinterp:
                yinterp = ''
            if isinstance(yframe, list) and not yframe:
                yframe = ''
            if isinstance(yinterp, str) and isinstance(yframe, str):
                # For now, ignore cases where xinterp or xframe is a list
                if isinstance(xframe, list):
                    msg_fmt = "Assuming xframe={assumed} instead of xframe={org}"
                    assumed_xframe = '' if not xframe else xframe[0]
                    msg = msg_fmt.format(assumed=assumed_xframe, org=xframe)
                    print("warning %s" % msg)
                    xframe = assumed_xframe
                if isinstance(xinterp, list):
                    msg_fmt = "Assuming xinterp={assumed} instead of xinterp={org}"
                    assumed_xinterp = '' if not xinterp else xinterp[0]
                    msg = msg_fmt.format(assumed=assumed_xinterp, org=xinterp)
                    print("warning %s" % msg)
                    xinterp = assumed_xinterp
                if isinstance(yaxislocation, list):
                    yaxislocation= 'left' if not yaxislocation else yaxislocation[0]
                if not isinstance(yaxislocation, str):
                    yaxislocation= 'left'
                xdatacolumn = ydatacolumn = ''
                pm.setPlotAxes(xaxis, yaxis, xdatacolumn, ydatacolumn,
                xframe, yframe, xinterp, yinterp,
                yaxislocation,
                False, plotindex, 0)
            else:
                # Handle yinterp, yframe and yaxislocation as parallel lists, which
                # 1. must have the same length
                # 2. must NOT contain empty strings, otherwise C++ vectors won't have the same length
                if isinstance(yinterp, list):
                    if isinstance(yframe, str):
                        # Allow usage: plotms(yinterp=['nearest','spline'],yframe='')
                        if not yframe:
                            yframe = 'icrs'
                        yframe = [yframe for i in yinterp]
                    else:
                        if len(yframe) != len(yinterp):
                            msg_fmt = "Length mismatch: yframe={0} and yinterp={1}"
                            msg = msg_fmt.format(yframe,yinterp)
                            raise RuntimeError(msg)
                    if isinstance(yaxislocation, str):
                        # Allow usage: plotms(yinterp=['nearest','spline'],yaxislocation='')
                        if not yaxislocation:
                            yaxislocation = 'left'
                        yaxislocation = [yaxislocation for i in yinterp]
                    else:
                        if len(yaxislocation) != len(yinterp):
                            msg_fmt = "Length mismatch: yaxislocation={0} and yinterp={1}"
                            msg = msg_fmt.format(yaxislocation,yinterp)
                            raise RuntimeError(msg)
                    # For now: enforce xframe=yframe, xinterp=yinterp in this case
                    print('warning enforcing xframe=yframe, xinterp=yinterp')
                    xdatacolumn = ydatacolumn = 'data'
                    if not xaxis:
                        xaxis = 'time'
                    for dataindex, (frame,interp,yaxisloc) in enumerate(zip(yframe,yinterp,yaxislocation)):
                        pm.setPlotAxes(xaxis, yaxis, xdatacolumn, ydatacolumn,
                                       frame, frame, interp, interp,
                                       yaxisloc,
                                       False, plotindex, dataindex)
                else:
                    raise RuntimeError('not yet implemented: yframe=list')
        else:
            if not yaxislocation or not isinstance(yaxislocation, str):
                yaxislocation='left'
            if not ydatacolumn or not isinstance(ydatacolumn, str):
                ydatacolumn=''
            pm.setPlotAxes(xaxis, yaxis, xdatacolumn, ydatacolumn,
                xframe, yframe, xinterp, yinterp,
                yaxislocation, False, plotindex, 0)
    else:
        # make ydatacolumn and yaxislocation same length as yaxis
        # and check that no duplicate y axes
        yAxisCount = len(yaxis)
        yDataCount = 0
        yLocationCount = 0
        if not isinstance(ydatacolumn, str):
            yDataCount = len(ydatacolumn)
        if not isinstance(yaxislocation, str):
            yLocationCount = len(yaxislocation)
        '''Make sure all the y-axis values are unique.'''
        uniqueY = True
        for i in range( yAxisCount ):
            yDataColumnI = ''
            if  i < yDataCount :
                yDataColumnI = ydatacolumn[i]
            for j in range(i):
                if yaxis[j] == yaxis[i] : # same axis, check datacolumn
                    yDataColumnJ = ''
                    if j < yDataCount:
                        yDataColumnJ = ydatacolumn[j]
                    if yDataColumnI == yDataColumnJ :
                        # same axis, same datacolumn!
                        uniqueY = False
                        break
            if not uniqueY :
                break
        if uniqueY:
            for i in range(yAxisCount):
                yDataColumn=''
                if i < yDataCount:
                    yDataColumn = ydatacolumn[i]
                yAxisLocation = 'left'
                if i < yLocationCount:
                    yAxisLocation = yaxislocation[i]
                if xaxis in ['ant-ra','ant-dec'] or yaxis[i]  in ['ant-ra','ant-dec']:
                    raise RuntimeError('currently not supported: multiple y-axes involving ant-ra or ant-dec')
                # Always make C++ ra/dec parameters vectors the same length as yaxis
                xframe = yframe = 'icrs'
                xinterp = yinterp = 'nearest'
                pm.setPlotAxes(xaxis, yaxis[i], xdatacolumn, yDataColumn,
                    xframe, yframe, xinterp, yinterp,
                    yAxisLocation,
                    False, plotindex, i)
        else :
            raise RuntimeError('Remove duplicate y-axes.')

    if showatm and showtsky:
        print('Warning: you have selected both showatm and showtsky.  Defaulting to showatm=True only.')
        showtsky = False
    if showatm or showtsky:  # check that xaxis is "", chan, or freq
        validxaxis = not xaxis or xaxis in ["channel", "frequency"]
        if not validxaxis:
            raise ValueError('xaxis must be channel or frequency for showatm and showtsky')
    if showimage and (not showatm and not showtsky):
        casalog.post('Defaulting to showimage=False because showatm and showtsky are False.', "WARN")
        showimage = False
    pm.setShowCurve(showatm, showtsky, showimage, False, plotindex)

    # Set selection
    if selectdata:
        pm.setPlotMSSelection(field, spw, timerange, uvrange, antenna, scan,
                              correlation, array, str(observation), intent,
                              feed, msselect, False, plotindex)
    else:
        pm.setPlotMSSelection('', '', '', '', '', '', '', '', '', '', '',
                              '', False, plotindex)

    # Set averaging
    if not averagedata:
        avgchannel = avgtime = ''
        avgscan = avgfield = avgbaseline = avgantenna = avgspw = False
        scalar = False
    if avgbaseline and avgantenna:
        raise ValueError('averaging over baselines is mutually exclusive with per-antenna averaging.')
    if avgchannel and (float(avgchannel) < 0.0):
        raise ValueError('cannot average negative number of channels')
    try:
        if avgtime and (float(avgtime) < 0.0):
            raise ValueError('cannot average negative time value')
    except ValueError:
        raise ValueError('avgtime value must be numerical string in seconds (no units)')
    pm.setPlotMSAveraging(avgchannel, avgtime, avgscan, avgfield, avgbaseline,
                          avgantenna, avgspw, scalar, False, plotindex)

    # Set transformations
    if not transform:
        freqframe=''
        restfreq=''
        veldef='RADIO'
        shift=[0.0,0.0]
    pm.setPlotMSTransformations(freqframe,veldef,restfreq,shift[0],shift[1],
                                False, plotindex)

    # Set calibration: string (filename or callib syntax)
    useCallib = False
    callibString = ''
    if isinstance(callib, list) and len(callib) > 0:
        if len(callib) == 1:
            callib0 = callib[0]
            if '=' in callib0: # callib is string of params
                useCallib = True
                callibString = callib0
            else: # callib is filename
                callibFile = callib0.strip()
                if len(callibFile) > 0:
                   callibFile = os.path.abspath(callib0)
                if os.path.exists(callibFile):
                    useCallib = True
                    callibString = callibFile
                else:
                    raise RuntimeError("callib file does not exist")
        else:  # callib is list of strings; make string of params
            useCallib = True
            callibString = ",".join(callib)
    pm.setPlotMSCalibration(useCallib, callibString, False, plotindex)

    # Set flag extensions; for now, some options here are not available
    # pm.setFlagExtension(extendflag, extcorrelation, extchannel, extspw,
    #    extantenna, exttime, extscans, extfield)
    extcorrstr=''
    if extcorr:
        extcorrstr='all'
    pm.setFlagExtension(extendflag, extcorrstr, extchannel)

    # Export range
    if not exprange:
        exprange='current'
    pm.setExportRange(exprange)

    # Set additional axes (iteration, colorization, etc.)
    # (Iteration)
    if not iteraxis:
        xselfscale = yselfscale = False
        xsharedaxis = ysharedaxis = False
    if rowindex >= gridrows or colindex >= gridcols: # 0-based index
        raise ValueError("row/col index out of range")
    if xsharedaxis and not xselfscale:
        raise ValueError("plots cannot share an x-axis unless they use the same x-axis scale.")
    if ysharedaxis and not yselfscale:
        raise ValueError( "plots cannot share a y-axis unless they use the same y-axis scale.")
    if xsharedaxis and gridrows < 2:
        casalog.post("Plots cannot share an x-axis when gridrows=1.", "WARN")
        xsharedaxis=False
    if ysharedaxis and gridcols < 2:
        casalog.post("Plots cannot share a y-axis when gridcols=1.", "WARN")
        ysharedaxis=False
    pm.setPlotMSIterate(iteraxis,rowindex,colindex,
                        xselfscale,yselfscale,
                        xsharedaxis,ysharedaxis,False,plotindex);

    # (Colorization)
    if coloraxis:
        pm.setColorAxis(coloraxis,False,plotindex)

    # Set custom symbol
    # Make the custom symbol params into lists
    if isinstance(customsymbol, bool) and customsymbol:
        customSymbolValue = customsymbol
        customsymbol=[customSymbolValue]
    if isinstance(symbolshape, str):
        symbolValue = symbolshape
        symbolshape=[symbolValue]
    if isinstance(symbolsize, int):
        symbolValue = symbolsize
        symbolsize=[symbolValue]
    if isinstance(symbolcolor, str):
        symbolValue = symbolcolor
        symbolcolor=[symbolValue]
    if isinstance(symbolfill, str):
        symbolValue = symbolfill
        symbolfill=[symbolValue]
    if isinstance(symboloutline, bool):
        symbolValue = symboloutline
        symboloutline=[symbolValue]

    if isinstance(customsymbol, list):
        customSymbolCount = len(customsymbol)
        for i in range(0,customSymbolCount):
            if  i >= len(symbolshape) or not symbolshape[i]:
                symbolShapeI = 'autoscaling'
            else:
                symbolShapeI = symbolshape[i]
            symbolShape = symbolShapeI

            if customsymbol[i]:
                if i >= len(symbolsize) or not symbolsize[i]:
                    symbolSizeI = 2
                else:
                    symbolSizeI = symbolsize[i]
                symbolSize = symbolSizeI

                if i >= len(symbolcolor) or not symbolcolor[i]:
                    symbolColorI = '0000ff'
                else:
                    symbolColorI = symbolcolor[i]
                symbolColor = symbolColorI

                if i >= len(symbolfill) or not symbolfill[i]:
                    symbolFillI = 'fill'
                else:
                    symbolFillI = symbolfill[i]
                symbolFill = symbolFillI

                if isinstance(symboloutline, bool):
                    symbolOutlineI = symboloutline
                elif isinstance(symboloutline, list):
                    if i >= len(symboloutline) or not symboloutline[i]:
                        symbolOutlineI = False
                    else:
                        symbolOutlineI = symboloutline[i]
                else:
                    symbolOutlineI = False
                symbolOutline = symbolOutlineI

            else:
                symbolSize = 2
                symbolColor = '0000ff'
                symbolFill = 'fill'
                symbolOutline = False
            pm.setSymbol(symbolShape, symbolSize, symbolColor,
                 symbolFill, symbolOutline, False, plotindex, i)

    # Set custom flagged symbol
    if isinstance(customflaggedsymbol, bool) and customflaggedsymbol:
        customSymbolValue = customflaggedsymbol
        customflaggedsymbol=[customSymbolValue]
    if isinstance(flaggedsymbolshape, str):
        symbolValue = flaggedsymbolshape
        flaggedsymbolshape=[symbolValue]
    if isinstance(flaggedsymbolsize, int):
        symbolValue = flaggedsymbolsize
        flaggedsymbolsize=[symbolValue]
    if isinstance(flaggedsymbolcolor, str):
        symbolValue = flaggedsymbolcolor
        flaggedsymbolcolor=[symbolValue]
    if isinstance(flaggedsymbolfill, str):
        symbolValue = flaggedsymbolfill
        flaggedsymbolfill=[symbolValue]
    if isinstance(flaggedsymboloutline, bool):
        symbolValue = flaggedsymboloutline
        flaggedsymboloutline=[symbolValue]

    if isinstance(customflaggedsymbol, list):
        customSymbolCount = len(customflaggedsymbol)
        for i in range(0,customSymbolCount):
            if i>=len(flaggedsymbolshape) or not flaggedsymbolshape[i]:
                flaggedSymbolShapeI = 'nosymbol'
            else:
                flaggedSymbolShapeI = flaggedsymbolshape[i]
            flaggedSymbolShape = flaggedSymbolShapeI

            if customflaggedsymbol[i]:
                if i >=len(flaggedsymbolsize) or not flaggedsymbolsize[i]:
                    flaggedSymbolSizeI = 2
                else:
                    flaggedSymbolSizeI = flaggedsymbolsize[i]
                flaggedSymbolSize = flaggedSymbolSizeI

                if i >=len(flaggedsymbolcolor) or not flaggedsymbolcolor[i]:
                    flaggedSymbolColorI = 'ff0000'
                else:
                    flaggedSymbolColorI = flaggedsymbolcolor[i]
                flaggedSymbolColor = flaggedSymbolColorI

                if i>=len(flaggedsymbolfill) or not flaggedsymbolfill[i]:
                    flaggedSymbolFillI = 'fill'
                else:
                    flaggedSymbolFillI = flaggedsymbolfill[i]
                flaggedSymbolFill = flaggedSymbolFillI

                if isinstance(flaggedsymboloutline, bool):
                    flaggedSymbolOutlineI = flaggedsymboloutline
                elif isinstance(flaggedsymboloutline, list):
                    if i>=len(flaggedsymboloutline) or not flaggedsymboloutline[i]:
                        flaggedSymbolOutlineI = False
                    else:
                        flaggedSymbolOutlineI = flaggedsymboloutline[i]
                else:
                    flaggedSymbolOutlineI = False
                flaggedSymbolOutline = flaggedSymbolOutlineI
            else:
                flaggedSymbolSize = 2
                flaggedSymbolColor = 'ff0000'
                flaggedSymbolFill = 'fill'
                flaggedSymbolOutline = False
            pm.setFlaggedSymbol(flaggedSymbolShape, flaggedSymbolSize,
                        flaggedSymbolColor, flaggedSymbolFill,
                        flaggedSymbolOutline, False, plotindex, i)

    # Connect the dots
    if not xconnector:
        xconnector = 'none'
    pm.setConnect(xconnector, timeconnector, False, plotindex)

    # Legend
    if not legendposition:
        legendposition = 'upperRight'
    pm.setLegend( showlegend, legendposition, False, plotindex )

    # Set various user-directed appearance parameters
    pm.setTitle(title, False, plotindex)
    pm.setTitleFont(titlefont, False, plotindex)
    pm.setXAxisLabel(xlabel, False, plotindex)
    pm.setXAxisFont(xaxisfont, False, plotindex)
    pm.setYAxisLabel(ylabel, False, plotindex)
    pm.setYAxisFont(yaxisfont, False, plotindex)
    pm.setGridParams(showmajorgrid, majorwidth, majorstyle, majorcolor,
                     showminorgrid, minorwidth, minorstyle, minorcolor,
                     False, plotindex)

    # Plot ranges
    if len(plotrange) == 0:
        plotrange=[0.0, 0.0, 0.0, 0.0]
    elif len(plotrange) != 4:
        raise ValueError('plotrange parameter has incorrect number of elements.')
    else:
        try:
            for i,val in enumerate(plotrange):
                plotrange[i] = float(val)
        except (TypeError, ValueError) as e:
            raise TypeError("plotrange elements must be numeric")
    xautorange = (plotrange[0] == 0) and (plotrange[1] == 0)
    yautorange = (plotrange[2] == 0) and (plotrange[3] == 0)
    pm.setXRange(xautorange, plotrange[0], plotrange[1], False, plotindex)
    pm.setYRange(yautorange, plotrange[2], plotrange[3], False, plotindex)

    # Page Header Items
    # Python keywords for specifying header items are defined in CAS-8082,
    # Erik's comment dated 9-jun-2016
    # Python / C++ header items keywords map
    # format is header_cpp_kw['python_keyword'] = 'c++_keyword', where
    # the c++ keyword is what's coded in PlotMSPageHeaderParam.h
    header_cpp_kw = {}
    header_cpp_kw['filename'] = 'filename'
    header_cpp_kw['ycolumn']  = 'y_columns'
    header_cpp_kw['obsdate']  = 'obs_start_date'
    header_cpp_kw['obstime']  = 'obs_start_time'
    header_cpp_kw['observer'] = 'obs_observer'
    header_cpp_kw['projid']   = 'obs_project'
    header_cpp_kw['telescope'] = 'obs_telescope_name'
    header_cpp_kw['targname'] = 'target_name'
    header_cpp_kw['targdir']  = 'target_direction'

    if isinstance(headeritems, str):
        cpp_headeritems = []
        for headeritem_word in headeritems.split(','):
            py_headeritem = headeritem_word.strip()
            if py_headeritem == "":
                continue
            if py_headeritem in header_cpp_kw:
                ccp_headeritem = header_cpp_kw[py_headeritem]
                cpp_headeritems.append(ccp_headeritem)
            else:
                casalog.post("Ignoring invalid page header item: " + py_headeritem, "WARN")

        pm.setPlotMSPageHeaderItems(','.join(cpp_headeritems), False, plotindex)

    # Update - ready to plot!
    plotUpdated = pm.update()

    if not plotUpdated:
        raise RuntimeError( "there was a problem updating the plot." )
    else:
        # write file if requested
        if plotfile:
            # kluge: isDrawing checks if *any* thread is running, could be cache
            # thread or drawing thread! Give it time for cache to finish...
            time.sleep(0.5)
            if (pm.isDrawing()):
                casalog.post("Waiting until drawing of the plot has completed before exporting it")
                while (pm.isDrawing()):
                    time.sleep(1.0)
            casalog.post("Exporting the plot to " + plotfile)
            pm.save( plotfile, expformat, verbose, highres, dpi, width, height)


def checkVariantString(name, param, valid_values):
    ''' check type and value of param (string or list) in valid_values list '''
    if isinstance(param, str):
        if valid_values and param not in valid_values:
            raise ValueError("invalid " + name + " value '" + param + "'")
    elif isinstance(param, list):
        for iparam in param:
            if not isinstance(iparam, str):
                raise TypeError("invalid " + name + " type, " + iparam + " should be string")
            if valid_values and iparam not in valid_values:
                raise ValueError("invalid " + name + " value '" + iparam + "'")
    else:
        raise TypeError("invalid " + name + " type, should be string or list")

def checkVariantBool(name, param):
    ''' check type of param (bool or list) '''
    if isinstance(param, bool):
        pass
    elif isinstance(param, list):
        for iparam in param:
            if not isinstance(iparam, bool):
                raise TypeError("invalid " + name + " type, " + iparam + " should be bool")
    else:
        raise TypeError("invalid " + name + " type, should be bool or list")

def checkVariantInt(name, param):
    ''' check type of param (int or list) '''
    if isinstance(param, int):
        pass
    elif isinstance(param, list):
        for iparam in param:
            if not isinstance(iparam, int):
                raise TypeError("invalid " + name + " type, " + iparam + " should be int")
    else:
        raise TypeError("invalid " + name + " type, should be int or list")
