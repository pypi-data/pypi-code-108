"""
Copyright (C) 2018-2022 John W. Williams

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from enum import Enum

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector

from .data import Tube, TubeData

class TubeEditor():
    """ Interface components based on TubeEditor.

    Interactive tool to draw mask on an image or image-like array.
    Adapted from matplotlib/examples/event_handling/poly_editor.py.
    """

    # set during initialization
    ax = None

    # selects which rectangle that is being edited ( 0 or 1)
    current_position = 0
    current_rects = []

    tube_data = None

    # state and configuration
    current_mode = None

    class Mode(Enum):
        CREATE = 1
        EDIT = 2
        ADJUST = 3
        DISP = 4

    def __init__(self, ss, td, te, ax, num_polys, num_slices,
                 num_times, poly_xy=None, max_ds=10):
        # initialize local variables
        self.showverts = True
        self.max_ds = max_ds
        self.num_slices = num_slices
        self.num_times = num_times

        self.ss = ss  # TODO: move main hotkey handling to SampleSlicer
        self.tube_data = td
        self.tube_extractor = te

        self.ax = ax
        self.ax.set_clip_on(False)

        # Disable matplotlib keyboard shortcuts
        plt.rcParams['keymap.back'] = ''
        plt.rcParams['keymap.forward'] = ''
        plt.rcParams['keymap.fullscreen'] = ''
        plt.rcParams['keymap.grid'] = ''
        plt.rcParams['keymap.home'] = ''
        plt.rcParams['keymap.pan'] = ''
        plt.rcParams['keymap.quit'] = ''
        plt.rcParams['keymap.save'] = ''
        plt.rcParams['keymap.xscale'] = ''
        plt.rcParams['keymap.yscale'] = ''
        plt.rcParams['keymap.zoom'] = ''

        self.rs = RectangleSelector(self.ax, self.create_line_select_callback,
                                    drawtype='box', useblit=True,
                                    button=[1, 3],  # don't use middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)

        # register callback events for the user interface
        self.key_press_cid = None
        self.canvas = ax.figure.canvas

        # switch to CREATE mode immediately
        self.set_mode(TubeEditor.Mode.DISP)
        self.key_press_cid = self.canvas.mpl_connect(
            'key_press_event', self.key_press_callback)

        self.set_position(0)
        self.draw_callback()

    #
    # methods to change the state (modify current tube and position)
    #

    # mode modification
    def set_mode(self, new_mode):
        #  - CREATE:
        #       - raw rectangle diagonal line in desired viewing plane (red line)
        #  - CREATE/EDIT:
        #       - click rectangle to select/modify -> change rectangle to color_selected
        #       - width, height change (opposite to fixed point) 
        #       - calculate rectangle object from lines, save lines for viewing
        #       - automatically create copy to seed rect1
        #  - CREATE/EDIT/ADJUST
        #       - translation: arrow keys (offset applies to selected rectangle)
        #       - hotkeys to dialate (+), contract (-), move (mouse1), pixel shift (udlr)
        #  - ANY
        #       - Escape/Enter key to release rectangle -> change to color_default
        self.current_mode = new_mode

        if new_mode == TubeEditor.Mode.CREATE:
            print("Changing to CREATE mode")
            # no rectangle
            # if self.key_press_cid is not None:
            #    self.canvas.mpl_disconnect(self.key_press_cid)
            self.key_press_cid = self.canvas.mpl_connect(
                'key_press_event', self.key_press_callback)

            if self.cid_pick is not None:
                self.canvas.mpl_disconnect(self.cid_pick)

            # set up to handle create events through the rectangle selector
            self.rs.set_active(True)

        elif new_mode == TubeEditor.Mode.EDIT:
            print("Changing to EDIT mode")
            # rectangle selected
            # set rectangle color to blue
            # handle key shortcuts
            # if self.key_press_cid is not None:
            self.rs.set_active(False)
            # if self.key_press_cid is not None:
            #    self.canvas.mpl_disconnect(self.key_press_cid)
            self.key_press_cid = self.canvas.mpl_connect(
                'key_press_event', self.key_press_callback)

        elif new_mode == TubeEditor.Mode.ADJUST:
            print("Changing to ADJUST mode")
            # rectangle selected
            # set rectangle color to orange
            # handle key shortcuts
            self.rs.set_active(False)
            canvas.mpl_connect('key_press_event', self.key_press_callback)

        elif new_mode == TubeEditor.Mode.DISP:
            print("Changing to DISPLAY mode")
            # if self.key_press_cid is not None:
            #    self.canvas.mpl_disconnect(self.key_press_cid)
            #    self.key_press_cid = None
            #rect.figure.canvas.mpl_connect('button_press_event', self.on_pick)
            #rect.figure.canvas.mpl_connect('pick_event', self.on_pick)
            self.rs.set_active(False)
            self.cid_pick = self.canvas.mpl_connect('pick_event', self.on_pick)
            self.select_tube(-1)

        self.draw_callback()

    def get_mode(self):
        return self.current_mode

    def get_selected_rect(self):
        cur_rect = None
        cur_tube = self.tube_data.get_tube()
        if cur_tube is not None and self.current_position == 0 or self.current_position == 1:
            cur_rect = cur_tube[self.current_position]
        return cur_rect

    #
    # visual display functions
    #

    def draw_callback(self, event=None, full_redraw=True):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        #backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axes]
       # items = enumerate(zip(lines, axes, backgrounds), start=1)
#        for j, (line, ax, background) in items:

        if full_redraw:
            self.canvas.draw()
#        self.canvas.restore_region(self.background)
#            line.set_ydata(np.sin(j*x + i/10.0))
        # ax.draw_artist(line)
        # fig.canvas.blit(ax.bbox)
#        for rect in self.current_rects:
 #           self.ax.draw_artist(rect)
        self.canvas.blit(self.ax.bbox)

    # update to a new internal index and redraw as necessary
    def select_tube(self, new_index):
        self.tube_data.select_tube(new_index)

        # if we actually are editing a tube change to edit mode
        if (new_index != -1):
            self.set_mode(TubeEditor.Mode.EDIT)

        self.draw_callback()

    def select_tube_obj(self, rect):
        new_idx = self.current_rects.index(rect)
        if new_idx != -1:
            self.select_tube(new_idx)

    # change from slice0 to a different slice
    def set_position(self, new_position):
        # 0 - rect0
        # 0 < x < 1 : between (interpolate?)
        # 1 - rect1

        # remove current rects from view
        for rect in self.current_rects:
            rect.remove()

        self.current_rects = self.tube_data.get_rects_at(new_position)

        # paint new rects
        for rect in self.current_rects:
            self.ax.add_patch(rect)

        self.current_position = new_position

        self.draw_callback(full_redraw=True)
        plt.draw()

    #
    # CREATE methods
    #

    # create new rectangle based on diagonal line
    def create_line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print(("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2)))
        print((" The button you used were: %s %s" %
              (eclick.button, erelease.button)))

        new_tube = self.tube_data.add_new_tube(
            x1, y1, x2, y2, angle=0.0, ax=self.ax)

        self.current_rects.append(new_tube[0])
        # add patch manually here
        self.ax.add_patch(new_tube[0])

        new_tube[0].set_picker(True)

        new_index = len(self.current_rects) - 1

        # immediately jump into edit mode (also redraws)
        self.select_tube(new_index)

        # TODO: kill rectangle selector after create
        self.rs.set_active(False)
    #
    # drawing an oriented rectangle
    #  - (possible on current_tube=0, current_index=max of any time-slice
    #
    # creation procedure:
    #  tN/2,s0 + sN - define rectangles (rect_r0,rect_r1) @ ((tN/2, s0),(tN/2,sN)) for rotation for everything
    #  copy rectangles (rect_r0,rect_r1) to (rect_c0, rect_c1), view across t0-tN,
    #       expand as necessary, use as crop for everything
    #
    #
    #  rect1 (t0,sN)
    #  - yellow clone of rect1 (is_validated == False)
    #  - click to select rect1 (is_validated = True)
    #  - only difference is symmetric dialation around the center to include regions
    #  - set center and angles for rectangle
    #  rect0 (tN,s0) and rect1 (tN,SN)
    #  - view

    # MAYBE v2
    #  - rotate rectangle around center (, for left, . for right)

    #
    # event callbacks for TubeEditor
    #

    def on_pick(self, event):
        #rect = event.artist
        #xdata, ydata = rect.get_data()
        #ind = event.ind
        #print('on pick line:', np.array([xdata[ind], ydata[ind]]).T)
        print("pick ", event.artist)
        if self.tube_data.get_tube() is None:
            self.select_tube_obj(event.artist)

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        print("press")
        ignore = not self.showverts or event.inaxes is None or event.button != 1
        if ignore:
            return
        self._ind = self.get_ind_under_cursor(event)

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        print("release")
        ignore = not self.showverts or event.button != 1
        if ignore:
            return
        self._ind = None

    # viewing procedure
    def key_press_callback(self, event):
        # TODO: move keyboard event handling to SampleSlicer or new class
        #  - scrolling to go slice-by-slice
        # print event.key
        'whenever a key is pressed'
        if event.key in ['Q', 'q'] and self.rs.active:
            #print(' RectangleSelector deactivated.')
            self.rs.set_active(False)
        if event.key in ['A', 'a'] and not self.rs.active:
            #print(' RectangleSelector activated.')
            self.rs.set_active(True)
        # if not event.inaxes:
        #    return

        #  - CREATE:
        #       - draw rectangle diagonal line in desired viewing plane (red line)
        #  - CREATE/EDIT/ADJUST
        #       - translation: arrow keys (offset applies to selected rectangle)
        #       - hotkeys to dialate (+), contract (-), move (mouse1), pixel shift (udlr)
        #  - ANY

        # movement hotkeys
        #  - Home -> jump to slice0, End -> Jump to sliceN
        #  - Page down -> go down in time, Page up -> go up in time
        if event.key == "home":
            self.ss.go_home()
        elif event.key == "end":
            self.ss.go_end()

        #  - CREATE/EDIT:
        #       - click rectangle to select/modify -> change rectangle to color_selected
        #       - width, height change (opposite to fixed point): 8462 (numpad)
        #       - calculate rectangle object from lines, save lines for viewing
#        if self.get_mode == TubeEditor.Mode.CREATE or TubeEditor.Mode.EDIT:

        if self.get_mode() == TubeEditor.Mode.ADJUST or self.get_mode() == TubeEditor.Mode.EDIT:
            # print "Processing ADJUST EDIT events"
            # rectangle selected
            # set rectangle color to orange
            # handle key shortcuts
            # TRANSLATE: arrow keys (offset applies to selected rectangle)
            # DIALATE (+), contract (-), move (mouse1), pixel shift (udlr)
            # if event.key == '+':
            #    self.dialate_rect(dir='out')
            # elif event.key == '-':
            #    self.dialate_rect(dir='in')

            cur_pos = self.current_position
            if cur_pos == 0 or cur_pos == 1:
                cur_pos = int(cur_pos)
                # translation
                if event.key == 'up':
                    self.tube_data.get_tube().translate_end(dir='up', pos=cur_pos)
                elif event.key == 'down':
                    self.tube_data.get_tube().translate_end(dir='down', pos=cur_pos)
                elif event.key == 'left':
                    self.tube_data.get_tube().translate_end(dir='left', pos=cur_pos)
                elif event.key == 'right':
                    self.tube_data.get_tube().translate_end(dir='right', pos=cur_pos)

                if event.key == 'j':
                    self.tube_data.get_tube().translate_end(dir='up', pos=cur_pos, pix=10)
                elif event.key == 'k':
                    self.tube_data.get_tube().translate_end(dir='down', pos=cur_pos, pix=10)
                elif event.key == 'h':
                    self.tube_data.get_tube().translate_end(dir='left', pos=cur_pos, pix=10)
                elif event.key == 'l':
                    self.tube_data.get_tube().translate_end(dir='right', pos=cur_pos, pix=10)

                # rotation
                elif event.key == ',':
                    self.tube_data.get_tube().rotate_rect(dir='counterclockwise')
                elif event.key == '.':
                    self.tube_data.get_tube().rotate_rect(dir='clockwise')
                elif event.key == 'm':
                    self.tube_data.get_tube().rotate_rect(dir='counterclockwise', degs=5)
                elif event.key == '/':
                    self.tube_data.get_tube().rotate_rect(dir='clockwise', degs=5)

                elif event.key == 'b':
                    self.tube_data.get_tube().go_back()
                elif event.key == 'e':
                    self.tube_extractor.get_fixed_tube(self.tube_data.get_tube(),
                                                       self.ss.image_3d, display=True)

                    # rectangle should exist
                # WIDTH, HEIGHT change (opposite to fixed point): 8462 (numpad)
                # print "Expanding rect"

                # expansion / dialation
                elif event.key == 'u':
                    self.tube_data.get_tube().expand_rect(dir='up')
                elif event.key == 'o':
                    self.tube_data.get_tube().expand_rect(dir='right')
                elif event.key == 'i':
                    self.tube_data.get_tube().expand_rect(dir='down')
                elif event.key == 'y':
                    self.tube_data.get_tube().expand_rect(dir='left')

                # set up to handle create events through the rectangle selector

        if event.key == 'escape':
            self.set_mode(TubeEditor.Mode.DISP)

        if self.get_mode() == TubeEditor.Mode.DISP or self.get_mode() == TubeEditor.Mode.EDIT:
            if event.key == 'n':
                self.set_mode(TubeEditor.Mode.CREATE)
            elif event.key == 'p':
                self.tube_data.print_data()
            elif event.key == 'w':
                self.ss.save_microtubes()
            elif event.key == 'r':
                self.ss.load_microtubes()
            elif event.key == 'e':
                if self.ss.sub_sample < 1:
                    tube_idx = abs(self.ss.sub_sample)
                    self.tube_extractor.get_fixed_tube(self.tube_data.microtubes[tube_idx],
                                                       self.ss.image_3d, display=True)

        self.draw_callback()
