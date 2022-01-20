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

import numpy as np
import matplotlib
# matplotlib.use('TKAgg')
from matplotlib.widgets import Slider, Button, RadioButtons
from functools import partial
import matplotlib.pyplot as plt

import imread  # support metadata for hyperstack

# for memory usage
import os
import sys          # for stdout
import subprocess
import psutil
import glob     # for getting sample paths
import distutils.dir_util
import logging
from datetime import datetime

from .tube import TubeData, TubeExtractor

# provides an interface for slicing a sample and outputting all of the data (+3d)
# SampleSlicer imports and manages the images from the sample set and
# configures the TubeEditor


class SampleSlicer():
    """ The main class that manage the actual work for slicing samples. """

    # all of this data is set upon initial import and setup
    sample_path = None  # path to data for current sample
    num_tubes = -1
    num_slices = -1
    num_times = -1

    current_tube = 0    # current tube being measured
    current_slice = 0   # current index being viewed
    current_time = 0    # current time being viewed

    sample_path = None
    sample_pat = None
    sample_img = None
    sub_sample = 1


    image_3d = None
    imagelist = None

    tube_data = None

    # main mask creator used to modify tubegons
    mc = None

    # matplotlib drawing stuff
    # plt = None  # main plot object
    fix = None
    ax = None

    def __init__(self, sample_path,
                 sample_pat,
                 sample_img,
                 output_path,
                 sub_sample,
                 microtubes_json,
                 batch_generate=False,
                 tube_idx_offset=0,
                 center_time_idx_offset=0):

        self.sample_path = sample_path
        self.sample_pat = sample_pat
        self.sample_img = sample_img
        self.output_path = output_path
        self.sub_sample = sub_sample
        self.microtubes_json = microtubes_json
        self.tube_idx_offset = tube_idx_offset
        self.center_time_idx_offset = center_time_idx_offset
        self.time_images = []

        root_log = logging.getLogger()
        root_log.setLevel(logging.DEBUG)
        #root_log.propagate = True

        # output general progress information to stdout
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.DEBUG)
        root_log.addHandler(sh)
        #sh.propagate = True

        # if this is a batch operation, write out a log
        if batch_generate == True:
            log_filename = self.output_path + datetime.now().strftime('log_%Y%m%d-%H%M.log')
            logging.info(
                "Writing out processing log to: {}".format(log_filename))

            # configure output file to be more verbose
            fh = logging.FileHandler(log_filename)
            fh.setLevel(logging.DEBUG)
            #fh.propagate = True
            root_log.addHandler(fh)

        logging.info("Batch generate: {}".format(batch_generate))

        # load times from
        self.sample_time_paths = sorted(
            glob.iglob(
                self.sample_path +
                "/" +
                self.sample_pat))
        self.num_times = len(self.sample_time_paths)
        logging.info(
            "Found {} times for the sample specified".format(
                self.num_times))

        self.tube_data = TubeData()  # need to initialize first to import data into

        microtubes_loaded = self.load_microtubes()

        # microtubes must be loaded in order to batch generate
        if batch_generate == True and microtubes_loaded == False:
            logging.info("Error: No microtubes definition file found. Use the editor mode (batch_generate = False) to define microtubes or otherwise provide the {} file for the sample.".format(microtubes_json))
            logging.info("Exiting.")
            return

        self.initialize(batch=batch_generate, sub_sample=sub_sample)

    """
        assumes a sample directory of:
            - sample
                - time0 - 36
                    - slice0 <- 44 microtubes ->  tube N
                    - slice1
                    ...
                    - sliceN <- tube
                    - N = 2160
                - time1
                    - slice0
                    - slice1
                    ...
                - timeN
                    - slice0 <- tube
                    - slice1
                    ...
                    - sliceN <- tube
            - sample1 - 45
                - time0
                    - slice0 <- 28 microtubes
                    - slice1
                    ...
                - time1
                    - slice0
                    - slice1
                    ...
                N = 2160
            ...

    """

    def initialize(self, batch=False, sub_sample=10):
        self.process = psutil.Process(os.getpid())
        logging.info(
            "Starting memory used: {} MB".format(
                self.process.memory_info().rss >> 20))

        if batch == False:
            logging.info("Using a subsample of {}".format(sub_sample))
            # import all the datasets subsampled for faster viewing
            self.import_data(sub_sample=sub_sample, store=True)

            # set initial time to look at
            #if sub_sample > 1 or True:
            self.image_3d = self.time_images[0]

            # set up main interface
            self.setup_matplotlib()

            # configure tube_extractor for testing and visualizing extractions
            self.tube_extractor = TubeExtractor(self, self.ax)

            # set up graphics
            self.tube_data.set_ax(self.ax)
            assert(self.ax is not None)
            self.fig.canvas.mpl_connect('scroll_event', self.onscroll)

            from .tube import TubeEditor

            # use TubeEditor to define and manipulate tubes
            self.mc = TubeEditor(self,
                                 self.tube_data,
                                 self.tube_extractor,
                                 self.ax,
                                 self.num_tubes,
                                 self.num_slices,
                                 self.num_times)

            # let user control from here
            plt.show()
        else:
            # configure tube_extractor for testing and visualizing extractions
            self.tube_extractor = TubeExtractor(self)

            logging.info(
                "Performing batch generation of microtubes from sample")
            self.batch_generate()

    def batch_generate(self):
        # for sample, load microtubes if exists
        #self.import_data(sub_sample = 1, store = False)
        #self.num_slices = 2178
        #self.output_hyperstacks()  # uncomment for hyperstack only
        #return  # uncomment for hyperstack only

        # load first time and apply microtube rotations
        for idx_time, path in enumerate(self.sample_time_paths):

            #logging.info("Loading data for time {} from {}".format(idx_time, path))
            self.load_data_at_time(idx_time, sub_sample=1, store=False)

            logging.info(
                "Memory after import: {} MB".format(
                    self.process.memory_info().rss >> 20))

            time_name = os.path.basename(path)

            logging.info("Running extraction for {} loaded tubes".format(
                len(self.tube_data.microtubes)))

            # for each defined tube, extract views and output
            for idx_tube, tube in enumerate(self.tube_data.microtubes):
                logging.info(
                    "Extracting Tube_{} from time {}".format(
                        idx_tube + self.tube_idx_offset, idx_time))
                # get top view and output stack
                fixed_tube_z = self.tube_extractor.get_fixed_tube(
                    tube, self.image_3d, display=False)

                for view in ['z', 'x']:
                    fixed_tube_view = fixed_tube_z

                    # re-index from y,x,z to y,z,x
                    if view == 'x':
                        fixed_tube_view = np.moveaxis(fixed_tube_z, 1, 2)

                    view_path = "{}/Tube_{:03d}/{}/{}/".format(self.output_path,
                                                               idx_tube + self.tube_idx_offset,
                                                               view,
                                                               time_name)

                    # output each of the views for this tube (with metadata)
                    self.output_img_to_stack(fixed_tube_view, view_path)

            logging.info("Finished time {}".format(idx_time))
            #logging.info("Removing previous time image from memory.")

            # call del on the loaded time so we can reuse this memory
            del self.image_3d

        self.output_hyperstacks()

    def output_hyperstacks(self):

        logging.info("Generating hyperstacks from output slices")
        # go back over the tubes and generate hyperstacks
        # output hyperstacks with default views
        for idx_tube, tube in enumerate(self.tube_data.microtubes):
            # run tiffcp to generate stacks for each view
            # for view in ['z','x']: #Use this line (instead of next) to make
            # hyperstacks in z and x directions.

            test_output_path = "{}/hyperstacks/Tube_hs_x_{tube_idx:03d}.tif".format(self.output_path,
                                                                                    tube_idx=idx_tube + self.tube_idx_offset)

            # skip if already exists
            if os.path.exists(test_output_path):
                print(("Skipping generation of existing {}".format(test_output_path)))
                continue

            for view in ['x']:
                hyperstack_slice_paths = []

                #logging.info(self.num_slices, self.num_times)
                # generate array of all slices in order
                for time_idx, time_path in enumerate(self.sample_time_paths):
                    time_name = os.path.basename(time_path)
                    slice_path = "image_*.tif"
                    hyperstack_slice_paths.append(slice_path)

                    full_output_path = "{}/Tube_{:03d}/{}/{}/".format(self.output_path,
                                                                      idx_tube + self.tube_idx_offset,
                                                                      view,
                                                                      time_name)

                    hyperstacks_dir = self.output_path + "/hyperstacks"
                    if not os.path.exists(hyperstacks_dir):
                        os.mkdir(hyperstacks_dir)

                    logging.debug(full_output_path)
                    # run tiffcp command to generate hyperstack
                    cmd = "bash -c \"tiffcp -a -c zip image_*.tif ../../../hyperstacks/Tube_hs_{view}_{tube_idx:03d}.tif\"".format(
                        view=view,
                        tube_idx=idx_tube + self.tube_idx_offset)

                    logging.debug(cmd)
                    r = subprocess.Popen(cmd, shell=True, cwd=full_output_path)
                    r.wait()
                    if r != 0:
                        try:
                            raise IOError('tiffcp call failed')
                        except BaseException:
                            pass
                #shutil.copy('{tmp_dir}/stacked.tiff'.format(tmp_dir=tmp_dir), oname)

    # write out the image to a stack of separate images with metadata
    def output_img_to_stack(self, image, path):
        # metata template specific to ImageJ to attach to each image
        _imagej_metadata = """ImageJ=1.51t
                            images={nr_images}
                            slices={nr_slices}
                            frames={nr_frames}
                            hyperstack=true
                            loop=false"""

        num_slices = image.shape[2]

        metadata = _imagej_metadata.format(
            nr_images=num_slices * self.num_times,
            nr_slices=num_slices,
            nr_frames=self.num_times)

        for idx in range(num_slices):
            output_path = "{}/image_{:04d}.tif".format(
                path, idx, self.tube_idx_offset)
            distutils.dir_util.mkpath(path)  # make path if it doesn't exist
            imread.imsave(output_path, image[:, :, idx], metadata=metadata)

    # load data at a particualr time index
    def load_data_at_time(self, time_idx, sub_sample=1, store=False):
        filename = self.sample_time_paths[time_idx]
        logging.info(
            "Loading time index {} from {}".format(
                time_idx, os.path.basename(filename)))

        crop_region = None

        if sub_sample < 0:
            tube_index = abs(sub_sample)
            crop_region = self.tube_data.microtubes[tube_index].get_3d_region()
            sub_sample = 1

        # get slice filenames in folder
        slice_filenames = sorted(glob.iglob(filename + "/" + self.sample_img))
        if self.num_slices <= 1:
            self.num_slices = int(len(slice_filenames) / sub_sample)
            logging.debug(
                "Number of slices for image: {}".format(
                    self.num_slices))

        num_slice = 0
        num_sub_slice = 0
        first = True    # always execute loop on first pass

        # load each slice independently and append to array
        for slice_filename in slice_filenames:
            # sub sample data
            if not first and (num_slice % sub_sample) > 0:
                # logging.info("skipping")
                num_slice += 1
                continue
            # logging.info(slice_filename)
            new_slice = imread.imread(slice_filename)

            #logging.info("Got new slice: {}".format(new_slice.shape))
            if self.image_3d is None:
                # open first image to get image size
                self.rows, self.cols = new_slice.shape

                if crop_region is not None:
                    logging.debug(crop_region)
                    self.rows = crop_region[1][0]  # width
                    self.cols = crop_region[1][1]  # height

                # create empty numpy array as gray 8-bit
                self.image_3d = np.empty((self.num_slices, self.rows, self.cols),
                                         dtype=np.uint8)

            # if not cropping then load everything
            if crop_region is None:
                # store data in the 3d array
                self.image_3d[num_sub_slice] = new_slice
            else:
                # if cropping then load data relevant to the tube
                ((y, x, z), (h, w, d)) = crop_region
                self.image_3d[num_sub_slice] = new_slice[y: y + h, x: x + w]

            num_sub_slice += 1
            num_slice += 1
            first = False

        #
        if self.image_3d is not None:
            # transform from z,x,y to y,x,z
            self.image_3d = np.moveaxis(self.image_3d, 0, 2)
            logging.debug(
                "Imported time with shape {}".format(
                    self.image_3d.shape))
            self.tube_data.set_depth(
                len(slice_filenames),
                self.image_3d.shape[2])
            print("STORE: {}".format(store))
            if store == True:
                self.time_images.append(self.image_3d)
                print(self.time_images)
                del self.image_3d

    # import all data for tube generation or load a particular data set
    def import_data(self, sub_sample=10, store=True):
        # import each time index 3d scan
        for idx, filename in enumerate(self.sample_time_paths):
            if sub_sample <= 0:
                self.load_data_at_time(idx, sub_sample=sub_sample, store=False)
                break
            else:
                # if in graphical mode load beginning middle and end
                if store == True:
                    if self.num_times > 3:
                        center_time_idx = int(
                            np.ceil(
                                self.num_times / 2)) + self.center_time_idx_offset
                        load_at_indexes = [0,
                                           center_time_idx,
                                           self.num_times - 1]
                        self.num_times = 3
                        for load_idx in load_at_indexes:
                            self.load_data_at_time(
                                load_idx, sub_sample=sub_sample, store=store)
                        return
                    else:
                        self.load_data_at_time(
                            idx, sub_sample=sub_sample, store=store)

        logging.info(
            "Memory after import: {} MB".format(
                self.process.memory_info().rss >> 20))

    #
    # save and load tube data
    #

    def save_microtubes(self):
        microtubes_full_json_path = self.output_path + "/" + self.microtubes_json
        logging.info("Saving microtubes to {}".format(
            microtubes_full_json_path))
        with open(microtubes_full_json_path, 'w') as json_file:
            self.tube_data.export_json(json_file)

    def load_microtubes(self):
        microtubes_full_json_path = self.output_path + "/" + self.microtubes_json

        ret_val = False
        # if there is a microtubes file specified and exists, import it
        if os.path.exists(microtubes_full_json_path):
            logging.info("Loading microtubes from {}".format(
                microtubes_full_json_path))
            with open(microtubes_full_json_path, 'r') as json_file:
                self.tube_data.import_json(json_file)
            ret_val = True

        return ret_val

        # self.mc.display_callback()

#    def state_machine(self):
#        # load initial data
#        ax.set_title('1. Set the tubegons for the first slice')
#        ax.set_title('use scroll wheel to navigate images')

    #
    # functions for manipulating interface and changing state
    #

    def set_tube(self, new_index):
        self.current_tube = new_index
        self.update()

    def set_slice(self, new_index):
        self.current_slice = new_index
        self.mc.set_position(
            float(
                self.current_slice) /
            float(
                self.num_slices -
                1))
        self.update()

    def set_time(self, new_index):
        self.current_time = new_index
        self.image_3d = self.time_images[self.current_time]
        self.update()

    # always called on any index change
    def update(self):
        self.im.set_data(self.image_3d[:, :, self.current_slice])
        self.ax.set_ylabel(
            'time {}\nslice {}'.format(
                self.current_time,
                self.current_slice))
        self.im.axes.figure.canvas.draw()

    # fixes the value of the slider and sets text
    def update_slider(self, slider):
        s = slider
        # make the slider integer
        s.val = round(s.val)
        s.poly.xy[2] = s.val, 1
        s.poly.xy[3] = s.val, 0
        s.valtext.set_text(s.valfmt % s.val)

    # called by TubeEditor to change state
    def go_home(self):
        self.set_slice(0)
#        self.slider_slice.val = float(self.current_slice)
        self.slider_slice.set_val(self.current_slice)
        self.update()

    # called by TubeEditor to change state
    def go_end(self):
        # TODO: fix weird polygon thing on end press without click first
        self.set_slice(self.num_slices - 1)
        self.slider_slice.val = float(self.current_slice)
        self.update_slider(self.slider_slice)
        # self.slider_slice.position_cursor(self.current_slice)
        self.update()

    #
    # external event handlers
    #

    def onscroll(self, event):
        #print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.current_slice = (self.current_slice + 1) % self.num_slices
        else:
            self.current_slice = (self.current_slice - 1) % self.num_slices

        self.slider_slice.val = float(self.current_slice)
        self.update_slider(self.slider_slice)
        self.update()
        #logging.info("EVENT: Scroll {} now @ {}".format(event.button, self.current_slice))

    #
    # slider handlers
    #

    # called when slider changed
    def tube_slider_changed(self, val):
        # update current viewed index based on slider
        self.update_slider(self.slider_tube)
        self.set_tube(int(self.slider_tube.val))

    # called when slider changed
    def slice_slider_changed(self, val):
        # update current viewed index based on slider
        self.update_slider(self.slider_slice)
        self.set_slice(int(self.slider_slice.val))

    # called when slider changed
    def time_slider_changed(self, val):
        # update current viewed index based on slider
        self.update_slider(self.slider_time)
        self.set_time(int(self.slider_time.val))

    #
    #
    # initialization functions
    #
    #

    def setup_matplotlib(self):
        """ set up main plot area and add space for slider below. """

        self.fig, self.ax = plt.subplots(1, 1)
        plt.subplots_adjust(bottom=0.15, right=0.95)

        axcolor = 'lightgoldenrodyellow'
#        tbidx = plt.axes([0.2, 0.15, 0.65, 0.03], facecolor=axcolor)
        axidx = plt.axes([0.2, 0.10, 0.65, 0.03], facecolor=axcolor)
        tmidx = plt.axes([0.2, 0.05, 0.65, 0.03], facecolor=axcolor)
        # ax2 = plt.subplot(111)
        # ax.imshow(img)

        # per tube modification
#        slider_tube = Slider(tbidx, 'uTube', 0, self.num_tubes - 1, valinit=0, valfmt='%i')
#        self.slider_tube = slider_tube
#        slider_tube.on_changed(self.tube_slider_changed)

        # create a slider to track and set the image index
        slider_idx = Slider(
            axidx,
            'Slice',
            0,
            self.num_slices - 1,
            valinit=0,
            valfmt='%i')
        self.slider_slice = slider_idx
        slider_idx.on_changed(self.slice_slider_changed)

        slider_time = Slider(
            tmidx,
            'Time',
            0,
            self.num_times - 1,
            valinit=0,
            valfmt='%i')
        self.slider_time = slider_time
        slider_time.on_changed(self.time_slider_changed)

        # current data being displayed
        self.im = self.ax.imshow(
            self.image_3d[:, :, self.current_slice], cmap='gray')
