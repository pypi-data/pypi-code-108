'''
make_interactive_svg.py

Example modified from https://matplotlib.org/3.1.1/gallery/user_interfaces/svg_histogram_sgskip.html

Functions takes in a matplotlib fig and plot filename.
Figure must have legend and lines.
Returns .svg plot file with interactive legend.

### Open the .svg in any browser ###
On Mac with Firefox:
$ open -a Firefox plot_svg.svg

On Mac with Google Chrome:
$ open -a Google\ Chrome plot_svg.svg


'''

import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from io import BytesIO
import json

def make_interactive_svg(fig, filename='plot_svg'):
    '''
    Produces a .svg plot file with an interactive legend
    Can click lines on or off when viewed in javascript-supporting browser.
    Inputs:
    fig      =  matplotlib figure object.
                Must have one and only one subplot, a legend, and a line object.
                Also, figure must not have been shown and closed before running
                this function, i.e no plt.show().
                This dumps the figure's contents or something and the lines
                cannot be found by the xml parser.
    filename =  full path to save file, with no extension.

    Example:

    import numpy as np
    import matplotlib.pyplot as plt
    from make_interactive_svg import *

    xx = np.linspace(0.0, 1.0, 50)
    yy = xx**(-xx)
    yy2 = 0.1*xx**(2)+1
    yy3 = 0.3*(xx-0.5)**(3)+1

    fig, ss = plt.subplots(1)
    ss.plot(xx, yy, lw=3, label='yy')
    ss.plot(xx, yy2, lw=3, label='yy2')
    ss.plot(xx, yy3, lw=3, label='yy3')

    ss.legend()

    make_interactive_svg(fig, 'example_svg')
    '''
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    ss = fig.get_axes()
    s1 = ss[0] # for now, just a single plot
    leg = s1.get_legend()
    containers = s1.lines


    # #print('Containers')
    for i, c in enumerate(containers):
         c.set_gid('lines_%d' % i)

    # Set ids for the legend patches
    # #print('Legend Lines')
    for i, t in enumerate(leg.get_lines()):
        t.set_pickradius(5)
        t.set_gid('leg_lines_%d' % i)

    # Set ids for the text patches
    # #print('Legend Text')
    for i, t in enumerate(leg.get_texts()):
        t.set_picker(5)
        t.set_gid('leg_text_%d' % i)

    f = BytesIO()
    plt.savefig(f, format="svg")

    # Create XML tree from the SVG file.
    tree, xmlid = ET.XMLID(f.getvalue())

    # Add attributes to the legend line objects.
    for i, t in enumerate(containers):
        # #print('lines_%d' % i)
        el = xmlid['lines_%d' % i]
        el.set('cursor', 'pointer')
        el.set('onclick', "toggle_hist(this)")

    # Add attributes to the legend line objects.
    for i, t in enumerate(leg.get_lines()):
        # #print('leg_lines_%d' % i)
        el = xmlid['leg_lines_%d' % i]
        el.set('cursor', 'pointer')
        el.set('onclick', "toggle_hist(this)")

    # Add attributes to the text objects.
    for i, t in enumerate(leg.get_texts()):
        # #print('leg_text_%d' % i)
        el = xmlid['leg_text_%d' % i]
        el.set('cursor', 'pointer')
        el.set('onclick', "toggle_hist(this)")

    # Create script defining the function `toggle_hist`.
    # We create a global variable `container` that stores the patches id
    # belonging to each histogram. Then a function "toggle_element" sets the
    # visibility attribute of all patches of each histogram and the opacity
    # of the marker itself.

    script = """
    <script type="text/ecmascript">
    <![CDATA[


    function toggle(oid, attribute, values) {
        /* Toggle the style attribute of an object between two values.

        Parameters
        ----------
        oid : str
          Object identifier.
        attribute : str
          Name of style attribute.
        values : [on state, off state]
          The two values that are switched between.
        */
        var obj = document.getElementById(oid);
        var a = obj.style[attribute];

        a = (a == values[0] || a == "") ? values[1] : values[0];
        obj.style[attribute] = a;
        }

    function toggle_hist(obj) {

        var num = obj.id.split("_").pop();

        toggle('lines_' + num.toString(), 'opacity', [1, 0]);
        toggle('leg_lines_' + num.toString(), 'opacity', [1, 0.2]);
        toggle('leg_text_' + num.toString(), 'opacity', [1, 0.5]);

        }
    ]]>
    </script>
    """ #% json.dumps(hist_patches)

    # Add a transition effect
    css = tree.getchildren()[0][0]
    css.text = css.text + "g {-webkit-transition:opacity 0.4s ease-out;" + \
        "-moz-transition:opacity 0.4s ease-out;}"

    # Insert the script and save to file.
    tree.insert(0, ET.XML(script))

    print('Saving file as {}.svg'.format(filename))
    ET.ElementTree(tree).write('{}.svg'.format(filename))
    return

def make_interactive_svg_multiple_subplots(fig, filename='plots_svg'):
    '''
    Produces a .svg plot file with an interactive legend for plots with multiple
    subplots but only one legend.
    Can click lines on or off when viewed in javascript-supporting browser.
    Inputs:
    fig      =  matplotlib figure object.
                Must have one and only one subplot, a legend, and a line object.
                Also, figure must not have been shown and closed before running
                this function, i.e no plt.show().
                This dumps the figure's contents or something and the lines
                cannot be found by the xml parser.
    filename =  full path to save file, with no extension.

    Example:

    import numpy as np
    import matplotlib.pyplot as plt
    from make_interactive_svg import *

    xx = np.linspace(0.0, 1.0, 50)
    yy = xx**(-xx)
    yy2 = 0.1*xx**(2)+1
    yy3 = 0.3*(xx-0.5)**(3)+1

    fig, ss = plt.subplots(2)
    s1 = ss[0]
    s2 = ss[1]

    s1.plot(xx, yy, lw=3, label='yy')
    s1.plot(xx, yy2, lw=3, label='yy2')
    s1.plot(xx, yy3, lw=3, label='yy3')

    s2.plot(xx, -yy, lw=3, ls='--', alpha=0.5, label='-yy')
    s2.plot(xx, -yy2, lw=3, ls='--', alpha=0.5, label='-yy2')
    s2.plot(xx, -yy3, lw=3, ls='--', alpha=0.5, label='-yy3')

    s1.legend()

    make_interactive_svg_multiple_subplots(fig, 'example_multiple_subplots_svg')

    '''
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    ss = fig.get_axes()
    for s in ss:
        if s.get_legend() is not None:
            leg = s.get_legend()

    for j, s in enumerate(ss):
        containers = s.lines
        for i, c in enumerate(containers):
             c.set_gid('lines_%d_%d' %(j, i))

    # Set ids for the legend patches
    for i, t in enumerate(leg.get_lines()):
        #print(i)
        t.set_picker(5)
        t.set_gid('leg_lines_%d' % i)

    # Set ids for the text patches
    for i, t in enumerate(leg.get_texts()):
        t.set_picker(5)
        t.set_gid('leg_text_%d' % i)

    f = BytesIO()
    plt.savefig(f, format="svg")

    # Create XML tree from the SVG file.
    tree, xmlid = ET.XMLID(f.getvalue())

    # Add attributes to the legend line objects.
    for j, s in enumerate(ss):
        for i, c in enumerate(containers):
            el = xmlid['lines_%d_%d' %(j, i)]
            el.set('cursor', 'pointer')
            el.set('onclick', "toggle_hist(this)")

    # Add attributes to the legend line objects.
    for i, t in enumerate(leg.get_lines()):
        el = xmlid['leg_lines_%d' % i]
        el.set('cursor', 'pointer')
        el.set('onclick', "toggle_hist(this)")

    # Add attributes to the text objects.
    for i, t in enumerate(leg.get_texts()):
        el = xmlid['leg_text_%d' % i]
        el.set('cursor', 'pointer')
        el.set('onclick', "toggle_hist(this)")

    # Create script defining the function `toggle_hist`.
    # We create a global variable `container` that stores the patches id
    # belonging to each histogram. Then a function "toggle_element" sets the
    # visibility attribute of all patches of each histogram and the opacity
    # of the marker itself.

    toggle_str = ''
    for j, s in enumerate(ss):
        toggle_str = "{}toggle('lines_' + {} + '_' + num, 'opacity', [1, 0]);\n        ".format(toggle_str, j)
    #print(toggle_str)

    script = """
    <script type="text/ecmascript">
    <![CDATA[


    function toggle(oid, attribute, values) {
        /* Toggle the style attribute of an object between two values.

        Parameters
        ----------
        oid : str
          Object identifier.
        attribute : str
          Name of style attribute.
        values : [on state, off state]
          The two values that are switched between.
        */
        var obj = document.getElementById(oid);
        var a = obj.style[attribute];

        a = (a == values[0] || a == "") ? values[1] : values[0];
        obj.style[attribute] = a;
        }

    function toggle_hist(obj) {

        var num = obj.id.split("_").pop();

        toggle('leg_lines_' + num, 'opacity', [1, 0.2]);
        toggle('leg_text_' + num, 'opacity', [1, 0.5]);
        %s


        }
    ]]>
    </script>
    """%(toggle_str)

    # Add a transition effect
    css = tree.getchildren()[0][0]
    css.text = css.text + "g {-webkit-transition:opacity 0.4s ease-out;" + \
        "-moz-transition:opacity 0.4s ease-out;}"

    # Insert the script and save to file.
    tree.insert(0, ET.XML(script))

    print('Saving file as {}.svg'.format(filename))
    ET.ElementTree(tree).write('{}.svg'.format(filename))
    return
