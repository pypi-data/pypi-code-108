# matplotlib defaults
# Author: Arvid Hahné

from cycler import cycler
import matplotlib.pyplot as plt

# font sizes
xsmall = 10
small = 14
medium = 18
large = 21

# rgb colors to floats for matplotlib and plotly
white = tuple(ti/255 for ti in (255, 255, 255))
light_blue = tuple(ti/255 for ti in (63, 141, 197))
blue = tuple(ti/255 for ti in (37, 111, 179))
dark_blue = tuple(ti/255 for ti in (0, 17, 70))
yellow = tuple(ti/255 for ti in (252, 190, 31))
orange = tuple(ti/255 for ti in (238, 92, 43))
red = tuple(ti/255 for ti in (181, 17, 51))
green = tuple(ti/255 for ti in (13, 112, 52))
grey = tuple(ti/255 for ti in (140, 148, 168))
light_grey = tuple(ti/255 for ti in (181, 198, 207))
dark_grey = tuple(ti/255 for ti in (63, 73, 77))
black = tuple(ti/255 for ti in (14, 18, 33))

# plot styles
style = {
    'histogram': {
        'basic': {
            'fill': False,
            'linewidth': 1,
            'hatch': '//',
        },
        'color': {
            'linewidth': 1,
        }
    }
}

### LINES
# See http://matplotlib.org/api/artist_api.html#module-matplotlib.lines for more

plt.rc('lines', linewidth=1) # line width in points
plt.rc('lines', linestyle='-')# solid line
#plt.rc('lines', color='C0')# has no affect on plot(); see axes.prop_cycle
#plt.rc('lines', marker='o')# the default marker
plt.rc('lines', markeredgewidth=0)# the line width around the marker symbol
plt.rc('lines', markersize=5)# markersize, in points
plt.rc('lines', markerfacecolor=black)# marker face color, in points
#plt.rc('lines', dash_joinstyle='miter')# miter|round|bevel
plt.rc('lines', dash_capstyle='round')# butt|round|projecting
#plt.rc('lines', solid_joinstyle='miter')# miter|round|bevel
plt.rc('lines', solid_capstyle='round')# butt|round|projecting
#plt.rc('lines', antialiased='True')# render lines in antialiased (no jaggies)
# The three standard dash patterns.  These are scaled by the linewidth.
plt.rc('lines', dashed_pattern=(10, 5))
plt.rc('lines', dashdot_pattern=(10, 3, 1, 3,))
plt.rc('lines', dotted_pattern=(1, 3))
#plt.rc('lines', scale_dashes=True
#plt.rc('markers', fillstyle:='full')# full|left|right|bottom|top|none

### PATCHES
# http://matplotlib.org/api/artist_api.html#module-matplotlib.patches

plt.rc('patch', linewidth=0.5)# edge width in points.
plt.rc('patch', facecolor='none')
plt.rc('patch', edgecolor=black)# if forced, or patch is not filled
plt.rc('patch', force_edgecolor='True')# True to always use edgecolor
#plt.rc('patch', antialiased='True')# render patches in antialiased (no jaggies)

### HATCHES
plt.rc('hatch', color=light_grey)
plt.rc('hatch', linewidth=0.5)

### Boxplot
plt.rc('boxplot', notch=False)
plt.rc('boxplot', vertical=True)
plt.rc('boxplot', whiskers=1)
plt.rc('boxplot', bootstrap=None)
plt.rc('boxplot', patchartist=True)
plt.rc('boxplot', showmeans=True)
plt.rc('boxplot', showcaps=True)
plt.rc('boxplot', showbox=True)
plt.rc('boxplot', showfliers=True)
plt.rc('boxplot', meanline=True)

plt.rc('boxplot.flierprops', color=red)
plt.rc('boxplot.flierprops', marker='+')
#plt.rc('boxplot.flierprops', markerfacecolor=white)
plt.rc('boxplot.flierprops', markeredgecolor=red)
plt.rc('boxplot.flierprops', markersize=7)
plt.rc('boxplot.flierprops', linestyle='none')
plt.rc('boxplot.flierprops', linewidth=1)

plt.rc('boxplot.boxprops', color=black)
plt.rc('boxplot.boxprops', linewidth=1)
plt.rc('boxplot.boxprops', linestyle='-')

#vertical lines Q1 & Q4
plt.rc('boxplot.whiskerprops', color=black)
plt.rc('boxplot.whiskerprops', linewidth=1)
plt.rc('boxplot.whiskerprops', linestyle='-')

#horizontal lines min & max
plt.rc('boxplot.capprops', color=black)
plt.rc('boxplot.capprops', linewidth=1)
plt.rc('boxplot.capprops', linestyle='-')

plt.rc('boxplot.medianprops', color=black)
plt.rc('boxplot.medianprops', linewidth=1)
plt.rc('boxplot.medianprops', linestyle='-')

plt.rc('boxplot.meanprops', color=blue)
plt.rc('boxplot.meanprops', marker=None)
#plt.rc('boxplot.meanprops', markerfacecolor=blue)
#plt.rc('boxplot.meanprops', markeredgecolor=white)
#plt.rc('boxplot.meanprops', markersize=7)
plt.rc('boxplot.meanprops', linestyle='solid')
plt.rc('boxplot.meanprops', linewidth=1)

### FONT
plt.rc('font', family='sans-serif') #serif', 'sans-serif', 'cursive', 'fantasy', and 'monospace'
plt.rc('font', style='normal') #normal (or roman), italic or oblique
plt.rc('font', variant='normal') #normal or small-caps
plt.rc('font', weight='normal') #normal, bold, bolder, lighter, 100, 200, 300, ..., 900
plt.rc('font', stretch='normal') #ultra-condensed, extra-condensed, condensed, semi-condensed, normal, semi-expanded, expanded, extra-expanded, ultra-expanded, wider, and narrower
plt.rc('font', size=small)
plt.rc('font', serif='Times')
#plt.rc('font', sans-serif='Tahoma')
plt.rc('font',**{'sans-serif':['Tahoma']})
#plt.rc('font', cursive='Zapf-Chancery')
#plt.rc('font', fantasy='Comic')
#plt.rc('font', monospace='Courier')

### TEXT
# http://matplotlib.org/api/artist_api.html#module-matplotlib.text for more
plt.rc('text', color=black)

### LaTeX customizations. See http://wiki.scipy.org/Cookbook/Matplotlib/UsingTex
#plt.rc('text', usetex='False')# use latex for all text handling.
#plt.rc('text', latex.unicode='False')# use "ucs" and "inputenc" LaTeX packages for handling unicode strings.
#plt.rc('text', latex.preamble='')# IMPROPER USE OF THIS FEATURE WILL LEAD TO LATEX FAILURES
#plt.rc('text', dvipnghack='None')# When dvipng doesn't handle alpha channel properly. True, False or None (=Guess)
#plt.rc('text', hinting='auto')# May be one of the following: 'none', 'auto', 'native', 'either'
#plt.rc('text', hinting_factor=8)# Specifies the amount of softness for hinting in the horizontal direction.
#plt.rc('text', antialiased='True')# If True (default), the text will be antialiased. This only affects the Agg backend.

# The following settings allow you to select the fonts in math mode. These settings are only used if mathtext.fontset is 'custom'. Note that this "custom" mode is unsupported and may go away in the future.
#plt.rc('mathtext', cal='cursive')
#plt.rc('mathtext', rm='serif')
#plt.rc('mathtext', tt='monospace')
#plt.rc('mathtext', it='serif:italic')
#plt.rc('mathtext', bf='serif:bold')
#plt.rc('mathtext', sf='sans')
#plt.rc('mathtext', fontset='dejavusans')# Should be 'dejavusans' (default), 'dejavuserif', 'cm' (Computer Modern), 'stix', 'stixsans' or 'custom'
#plt.rc('mathtext', fallback_to_cm=True)# When True, use symbols from the Computer Modern fonts when a symbol can not be found in one of the custom math fonts.
#plt.rc('mathtext', default='it')# The default font to use for math.

### AXES
# http://matplotlib.org/api/axes_api.html#module-matplotlib.axes
plt.rc('axes', facecolor=white)# axes background color
plt.rc('axes', edgecolor=black)# axes edge color
plt.rc('axes', linewidth=1)# edge linewidth
plt.rc('axes', grid=True)# display grid or not
plt.rc('axes.grid', axis='both')# which axis (x, y, both)
plt.rc('axes.grid', which='major')# major, minor or both

plt.rc('axes', titlesize=medium)# fontsize of the axes title
#plt.rc('axes', titlelocation='left')# title location (left, right, center)
#plt.rc('axes', titley=1.0)# pad between title and axis in points
plt.rc('axes', titlepad=10)# pad between title and axis in points
plt.rc('axes', labelsize=small)# fontsize of the x any y labels
#plt.rc('axes', labelpad=4.0)# space between label and axis
#plt.rc('axes', labelweight='normal')# weight of the x and y labels
plt.rc('axes', labelcolor=black)
#plt.rc('axes', axisbelow='line')# draw axis gridlines and ticks below patches (True); above patches but below lines ('line'); or above all (False)
#plt.rc('axes.formatter', limits='-7,')# use scientific notation if log10 of the axis range is smaller than the first or larger than the second
#plt.rc('axes.formatter', use_locale='False')# When True, format tick labels according to the user's locale. For example, use ',' as a decimal separator in the fr_FR locale.
#plt.rc('axes.formatter', use_mathtext='False')# When True, use mathtext for scientific notation.
#plt.rc('axes.formatter', useoffset='True')# If True, the tick label formatter will default to labeling ticks relative to an offset when the data range is small compared to the minimum absolute value of the data.
#plt.rc('axes.formatter', offset_threshold=4)# When useoffset is True, the offset will be used when it can remove at least this number of significant digits from tick labels.
plt.rc('axes.spines', left=True)  # display axis spines
plt.rc('axes.spines', bottom=True)
plt.rc('axes.spines', top=True)
plt.rc('axes.spines', right=True)
#plt.rc('axes', unicode_minus=True)# use unicode for the minus symbol rather than hyphen. See http://en.wikipedia.org/wiki/Plus_and_minus_signs#Character_codes
plt.rc('axes', prop_cycle=(cycler('color', [blue, light_blue, orange, yellow, green, dark_blue, red, grey]))) # color cycle for plot lines
plt.rc('axes', autolimit_mode='data')# How to scale axes limits to the data. Use "data" to use data limits, plus some margin. Use "round_numbers" move to the nearest "round" number
plt.rc('axes', xmargin='.05')# x margin. See `axes.Axes.margins`
plt.rc('axes', ymargin='.25')# y margin. See `axes.Axes.margins`
#plt.rc('polaraxes', grid='True')# display grid on polar axes
#plt.rc('axes3d', grid='True')# display grid on 3d axes

### DATES
# These control the default format strings used in AutoDateFormatter.
# Any valid format datetime format string can be used (see the python
# `datetime` for details).  For example using '%%x' will use the locale date representation
# '%%X' will use the locale time representation and '%%c' will use the full locale datetime
# representation.
# These values map to the scales:
#    {'year': 365, 'month': 30, 'day': 1, 'hour': 1/24, 'minute': 1 / (24 * 60)}
#plt.rc('date.autoformatter', year='%Y')
#plt.rc('date.autoformatter', month='%Y-%m')
#plt.rc('date.autoformatter', day='%Y-%m-%d')
#plt.rc('date.autoformatter', hour='%m-%d %H')
#plt.rc('date.autoformatter', minute='%d %H:%M')
#plt.rc('date.autoformatter', second='%H:%M:%S')
#plt.rc('date.autoformatter', microsecond='%M:%S.%f')

### TICKS
# see http://matplotlib.org/api/axis_api.html#matplotlib.axis.Tick
plt.rc('xtick', top=True)# draw ticks on the top side
plt.rc('xtick', bottom=True)# draw ticks on the bottom side
plt.rc('xtick', color=black)# color of the tick labels
plt.rc('xtick', labelsize=small)# fontsize of the tick labels
plt.rc('xtick', direction='inout')# direction: in, out, or inout

plt.rc('xtick.major', size=5)# major tick size in points
plt.rc('xtick.major', width=1)# major tick width in points
#plt.rc('xtick.major', pad=3.5)# distance to major tick label in points
plt.rc('xtick.major', top=True)# draw x axis top major ticks
plt.rc('xtick.major', bottom=True)# draw x axis bottom major ticks

plt.rc('xtick.minor', visible=False)# visibility of minor ticks on x-axis
#plt.rc('xtick.minor', size=0)# minor tick size in points
#plt.rc('xtick.minor', width=0.6)# minor tick width in points
#plt.rc('xtick.minor', pad=3.4)# distance to the minor tick label in points
#plt.rc('xtick.minor', top=False)# draw x axis top minor ticks
#plt.rc('xtick.minor', bottom=False)# draw x axis bottom minor ticks

plt.rc('ytick', left=True)# draw ticks on the left side
plt.rc('ytick', right=True)# draw ticks on the right side
plt.rc('ytick', color=black)# color of the tick labels
plt.rc('ytick', labelsize=small)# fontsize of the tick labels
plt.rc('ytick', direction='inout')# direction: in, out, or inout

#plt.rc('ytick.major', size=5)# major tick size in points
#plt.rc('ytick.major', width=0.8)# major tick width in points
#plt.rc('ytick.major', pad=3.5)# distance to major tick label in points
#plt.rc('ytick.major', left=True)# draw y axis left major ticks
#plt.rc('ytick.major', right=False)# draw y axis right major ticks

plt.rc('ytick.minor', visible=False)# visibility of minor ticks on y-axis
#plt.rc('ytick.minor', size=0)# minor tick size in points
#plt.rc('ytick.minor', width=0.6)# minor tick width in points
#plt.rc('ytick.minor', pad=3.4)# distance to the minor tick label in points
#plt.rc('ytick.minor', left=False)# draw y axis left minor ticks
#plt.rc('ytick.minor', right=False)# draw y axis right minor ticks

### GRIDS
plt.rc('grid', color=light_grey)# grid color
plt.rc('grid', linestyle='dotted')# solid
plt.rc('grid', linewidth=0.5)# in points
plt.rc('grid', alpha=0.5)# transparency, between 0.0 and 1.0

### Legend
plt.rc('legend', loc='best')
#plt.rc('legend', frameon=False)# if True, draw the legend on a background patch
#plt.rc('legend', framealpha=0.8)# legend patch transparency
#plt.rc('legend', facecolor='inherit')# inherit from axes.facecolor; or color spec
#plt.rc('legend', edgecolor=0.8)# background patch boundary color
#plt.rc('legend', fancybox=False)# if True, use a rounded box for the
                                 # legend background, else a rectangle
#plt.rc('legend', shadow='False')# if True, give background a shadow effect
#plt.rc('legend', numpoints=1)# the number of marker points in the legend line
#plt.rc('legend', scatterpoints=1)# number of scatter points
#plt.rc('legend', markerscale=1.0)# the relative size of legend markers vs. original
plt.rc('legend', fontsize=xsmall)
# Dimensions as fraction of fontsize:
#plt.rc('legend', borderpad=0.4)# border whitespace
#plt.rc('legend', labelspacing=0.5)# the vertical space between the legend entries
#plt.rc('legend', handlelength=2.0)# the length of the legend lines
#plt.rc('legend', handleheight=0.7)# the height of the legend handle
#plt.rc('legend', handletextpad=0.8)# the space between the legend line and legend text
#plt.rc('legend', borderaxespad=0.5)# the border between the axes and legend edge
#plt.rc('legend', columnspacing=2.0)# column separation

### FIGURE
# See http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure
plt.rc('figure', titlesize=large)# size of the figure title (Figure.suptitle())
#plt.rc('figure', titleweight='normal')# weight of the figure title
plt.rc('figure', figsize=(10,7))# figure size in inches
#plt.rc('figure', dpi=100)# figure dots per inch
plt.rc('figure', facecolor=white)# figure facecolor; 0.75 is scalar gray
plt.rc('figure', edgecolor=white)# figure edgecolor
#plt.rc('figure', autolayout='False')# When True, automatically adjust subplot
                            # parameters to make the plot fit the figure
#plt.rc('figure', max_open_warning=20)# The maximum number of figures to open through
                               # the pyplot interface before emitting a warning.
                               # If less than one this feature is disabled.
# The figure subplot parameters.  All dimensions are a fraction of the
#plt.rc('figure', subplot.left=0.125)# the left side of the subplots of the figure
#plt.rc('figure', subplot.right=0.9)# the right side of the subplots of the figure
#plt.rc('figure', subplot.bottom=0.11)# the bottom of the subplots of the figure
#plt.rc('figure', subplot.top=0.88)# the top of the subplots of the figure
#plt.rc('figure', subplot.wspace=0.2)# the amount of width reserved for blank space between subplots,
                                 # expressed as a fraction of the average axis width
#plt.rc('figure', subplot.hspace=0.2)# the amount of height reserved for white space between subplots,
                                 # expressed as a fraction of the average axis height
### IMAGES
#plt.rc('image', aspect='equal')# equal | auto | a number
#plt.rc('image', interpolation='nearest')# see help(imshow) for options
#plt.rc('image', cmap='viridis')# A colormap name, gray etc...
#plt.rc('image', lut=256)# the size of the colormap lookup table
#plt.rc('image', origin='upper')# lower | upper
#plt.rc('image', resample=
#plt.rc('image', composite_image='True')# When True, all the images on a set of axes are
                                  # combined into a single composite image before
                                  # saving a figure as a vector graphics file,
                                  # such as a PDF.
### CONTOUR PLOTS
#plt.rc('contour', negative_linestyle='dashed')# dashed | solid
#plt.rc('contour', corner_mask='True')# True | False | legacy

### ERRORBAR PLOTS
#plt.rc('errorbar', capsize=0)# length of end cap on error bars in pixels

### HISTOGRAM PLOTS
plt.rc('hist', bins='auto')# The default number of histogram bins.
                                  # If Numpy 1.11 or later is
                                  # installed, may also be `auto`
### SCATTER PLOTS
plt.rc('scatter', marker='o')# The default marker type for scatter plots.
### Agg rendering
### Warning: experimental, 2008/10/10
#plt.rc('agg', path.chunksize=0)# 0 to disable; values in the range
                                  # 10000 to 100000 can improve speed slightly
                                  # and prevent an Agg rendering failure
                                  # when plotting very large data sets,
                                  # especially if they are very gappy.
                                  # It may cause minor artifacts, though.
                                  # A value of 20000 is probably a good
                                  # starting point.
### SAVING FIGURES
#plt.rc('path', simplify='True')# When True, simplify paths by removing "invisible"
                        # points to reduce file size and increase rendering
                        # speed
#plt.rc('path', simplify_threshold=0.1)# The threshold of similarity below which
                                # vertices will be removed in the simplification
                                # process
#plt.rc('path', snap='True')# When True, rectilinear axis-aligned paths will be snapped to
                  # the nearest pixel when certain criteria are met.  When False,
                  # paths will never be snapped.
#plt.rc('path', sketch='None')# May be none, or a 3-tuple of the form (scale, length,
                    # randomness).
                    # *scale* is the amplitude of the wiggle
                    # perpendicular to the line (in pixels).  *length*
                    # is the length of the wiggle along the line (in
                    # pixels).  *randomness* is the factor by which
                    # the length is randomly scaled.
# the default savefig params can be different from the display params
# e.g., you may want a higher resolution, or to make the figure
# background white
#plt.rc('savefig', dpi='figure')# figure dots per inch or 'figure'
#plt.rc('savefig', facecolor='white')# figure facecolor when saving
#plt.rc('savefig', edgecolor='white')# figure edgecolor when saving
#plt.rc('savefig', format='png')# png, ps, pdf, svg
#plt.rc('savefig', bbox='standard')# 'tight' or 'standard'.
                                # 'tight' is incompatible with pipe-based animation
                                # backends but will workd with temporary file based ones:
                                # e.g. setting animation.writer to ffmpeg will not work,
                                # use ffmpeg_file instead
#plt.rc('savefig', pad_inches=0.1)# Padding to be used when bbox is set to 'tight'
#plt.rc('savefig', jpeg_quality:=95)# when a jpeg is saved, the default quality parameter.
#plt.rc('savefig', directory='~')# default directory in savefig dialog box,
                                # leave empty to always use current working directory
#plt.rc('savefig', transparent='False')# setting that controls whether figures are saved with a
                                # transparent background by default

# tk backend params
#plt.rc('tk', window_focus='False')# Maintain shell focus for TkAgg
# ps backend params
#plt.rc('ps', papersize='letter')# auto, letter, legal, ledger, A0-A10, B0-B10
#plt.rc('ps', useafm='False')# use of afm fonts, results in small files
#plt.rc('ps', usedistiller='False')# can be: None, ghostscript or xpdf
                                          # Experimental: may produce smaller files.
                                          # xpdf intended for production of publication quality files,
                                          # but requires ghostscript, xpdf and ps2eps
#plt.rc('ps', distiller.res=6000)# dpi
#plt.rc('ps', fonttype=3)# Output Type 3 (Type3) or Type 42 (TrueType)
# pdf backend params
#plt.rc('pdf', compression=6)# integer from 0 to 9
                       # 0 disables compression (good for debugging)
#plt.rc('pdf', fonttype=3)# Output Type 3 (Type3) or Type 42 (TrueType)
# svg backend params
#plt.rc('svg', image_inline='True')# write raster image data directly into the svg file
#plt.rc('svg', fonttype=''path'')# How to handle SVG fonts:
#    'none': Assume fonts are installed on the machine where the SVG will be viewed.
#    'path': Embed characters as paths -- supported by most SVG renderers
#    'svgfont': Embed characters as SVG fonts -- supported only by Chrome,
#               Opera and Safari
#plt.rc('svg', hashsalt='None')# if not None, use this string as hash salt
                               # instead of uuid4
# docstring params
#plt.rc('docstring', hardcopy=# set this when you want to generate hardcopy docstring
# Set the verbose flags.  This controls how much information
# matplotlib gives you at runtime and where it goes.  The verbosity
# levels are: silent, helpful, debug, debug-annoying.  Any level is
# inclusive of all the levels below it.  If your setting is "debug",
# you'll get all the debug and helpful messages.  When submitting
# problems to the mailing-list, please set verbose to "helpful" or "debug"
# and paste the output into your report.
#
# The "fileo" gives the destination for any calls to verbose.report.
# These objects can a filename, or a filehandle like sys.stdout.
#
# You can override the rc default verbosity from the command line by
# giving the flags --verbose-LEVEL where LEVEL is one of the legal
# levels, e.g., --verbose-helpful.
#
# You can access the verbose instance in your code
#   from matplotlib import verbose.
#plt.rc('verbose', level='silent')# one of silent, helpful, debug, debug-annoying
#plt.rc('verbose', fileo='sys.stdout')# a log filename, sys.stdout or sys.stderr
# Event keys to interact with figures/plots via keyboard.
# Customize these settings according to your needs.
# Leave the field(s) empty if you don't need a key-map. (i.e., fullscreen : '')
#plt.rc('keymap', fullscreen='f,')# toggling
#plt.rc('keymap', home='h,')# home or reset mnemonic
#plt.rc('keymap', back='left,')# forward / backward keys to enable
#plt.rc('keymap', forward='right,')#   left handed quick navigation
#plt.rc('keymap', pan='p')# pan mnemonic
#plt.rc('keymap', zoom='o')# zoom mnemonic
#plt.rc('keymap', save='s')# saving current figure
#plt.rc('keymap', quit='ctrl+w,')# close the current figure
#plt.rc('keymap', grid='g')# switching on/off a grid in current axes
#plt.rc('keymap', yscale='l')# toggle scaling of y-axes ('log'/'linear')
#plt.rc('keymap', xscale='L,')# toggle scaling of x-axes ('log'/'linear')
#plt.rc('keymap', all_axes='a')# enable all axes
# Control location of examples data files
#plt.rc('examples', directory='''')# directory to look in for custom installation
###ANIMATION settings
#plt.rc('animation', html=''none'')# How to display the animation as HTML in
                                   # the IPython notebook. 'html5' uses
                                   # HTML5 video tag.
#plt.rc('animation', writer='ffmpeg')# MovieWriter 'backend' to use
#plt.rc('animation', codec='h264')# Codec to use for writing movie
#plt.rc('animation', bitrate:='-1')# Controls size/quality tradeoff for movie.
                                   # -1 implies let utility auto-determine
#plt.rc('animation', frame_format:=''png'')# Controls frame format used by temp files
#plt.rc('animation', ffmpeg_path:=''ffmpeg'')# Path to ffmpeg binary. Without full path
                                   # $PATH is searched
#plt.rc('animation', ffmpeg_args:='''')# Additional arguments to pass to ffmpeg
#plt.rc('animation', avconv_path:=''avconv'')# Path to avconv binary. Without full path
                                   # $PATH is searched
#plt.rc('animation', avconv_args:='''')# Additional arguments to pass to avconv
#plt.rc('animation', mencoder_path:=
                                   # Path to mencoder binary. Without full path
                                   # $PATH is searched
#plt.rc('animation', mencoder_args:='''')# Additional arguments to pass to mencoder
#plt.rc('animation', convert_path:=''convert'')# Path to ImageMagick's convert binary.
                                   # On Windows use the full path since convert
                                   # is also the name of a system tool.
