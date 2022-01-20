#!/usr/bin/python

from sampleslicer import SampleSlicer

#
# Dataset configuration options
#

# path information for our sample set
sample0_path = "/home/john/sample0_full/"
sample0_pat = "rec201611*"
sample0_img = "*.tiff"

output_path = "/home/john/microtube_output/"

# or for a windows style path:
#output_path = "I:\Microtubes_all\sliceit\specimen201609\\"

# tube index offset (for naming output folders)
tube_idx_offset = 0  # first index is 32 = 32 + 0

# this is the filename used for reading and writing microtube definitons in the
# editor. when performing batch processing this is the file that will define
# the regions for the microtubes.
microtubes_json = "microtubes.json"

#
# TubeEditor GUI options
#

# Sub-sample the data set if desired
# This value must be set, set to 1 to disable sub-sampling the data when using
# the tube editor. This parameter is ignored in batch processing mode.
sub_sample = 10  # e.g. only open every 10 slices at a given time
center_time_idx_offset = 3  # offet of center time index to load

#
# SampleSlicer batch processing options
#

# If batch_generate is True then SampleSlicer will always load full datasets
# and output the fixed tubes to files in the corresponding folder structure.
batch_generate = False

def run():
    # run sample slicer with our image set
    SampleSlicer(   sample0_path,
                    sample0_pat,
                    sample0_img,
                    output_path,
                    sub_sample,
                    microtubes_json,
                    batch_generate=batch_generate,
                    tube_idx_offset=tube_idx_offset,
                    center_time_idx_offset=center_time_idx_offset)

if __name__ == "__main__":
    run()
