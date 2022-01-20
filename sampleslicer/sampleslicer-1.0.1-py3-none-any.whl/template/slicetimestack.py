
import subprocess
import glob
import os

output_path = "I:\Microtubes_all\sliceit\specimen201609\\"
overwrite = False

#   tube  direction slice#
do_list = (
    (4,     'z',    47),
    (15,    'x',    52),
    (5,     'z',    2127),
    (5,     'x',    1896),
    (29,    'x',    100),
    (13,    'x',    91),
    (24,    'x',    230)
)


for run in do_list:
    idx_tube = run[0]
    view = run[1]
    slice_idx = run[2]

    full_time_path = "./Tube_{:03d}/{}/*".format(idx_tube,
                                                 view)

    output_filename = "./time_slices/{tube_idx:03d}_ts_{view}_s{slice:04d}.tif".format(
            view=view, tube_idx=idx_tube, slice=slice_idx)

    # skip if already exists
    if os.path.exists(output_path + output_filename) and overwrite == False:
        print("Skipping generation of existing {}".format(output_filename))
        continue

    input_glob = "{time_path}/image_{slice:04d}.tif".format(time_path=full_time_path,
                                                            slice=slice_idx)

    input_filenames = sorted(glob.iglob(output_path + input_glob))
    num_slices = len(input_filenames)

    cmd = "bash -c \"tiffcp -a -c zip {input} {output_fname}\"".format(
        input=input_glob,
        output_fname=output_filename)

    print("Outputting hyperstack for tube {}, direction {}, slice {}".format(
            idx_tube, view, slice_idx))

    # print(cmd)
    r = subprocess.Popen(cmd, shell=True, cwd=output_path)
    r.wait()
    if r != 0:
        try:
            raise IOError('tiffcp call failed')
        except BaseException:
            pass

    # update metadata of the output file
    _imagej_metadata = """ImageJ=1.51t \
                    images={} \
                    slices={} \
                    frames={} \
                    hyperstack=false \
                    loop=false""".format(num_slices, num_slices, 1)

    print("Updating metadata to be stack with {} slices".format(num_slices))
    cmd_set = "bash -c \"tiffset -s 270 '{}' {}\"".format(
        _imagej_metadata, output_filename)
    # print cmd_set

    r = subprocess.Popen(cmd_set, shell=True, cwd=output_path)
    if r != 0:
        try:
            raise IOError('tiffset call failed')
        except BaseException:
            pass

