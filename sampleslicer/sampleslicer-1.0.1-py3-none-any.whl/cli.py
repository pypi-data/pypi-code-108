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

def main():

    import argparse
    parser = argparse.ArgumentParser(description=
"""
SampleSlicer is a tool written in python designed to enable the transformation
of arbitrary 3d or 4d datasets loaded as a set of image stacks.

The primary goal of SampleSlicer is to split up a large 4-dimensional dataset
into smaller samples using a graphical interface for defining the "tubes" of
data which may require cropping and a complex rotation.
""",
    formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-e', '--editor', dest='edit', action='store_const',
                        const=True, default=False,
                        help='Spawn the graphical editor.')

    parser.add_argument('-b', '--batch', dest='batch', action='store_const',
                        const=True, default=False,
                        help='Force batch processing of the entire dataset based on the "microtubes.json" file.')

    parser.add_argument('-g', '--generate-template', dest='gen', action='store_const',
                        const=True, default=False,
                        help=
"""Generate a new SampleSlicer template in the current directory (if none exists).

By default the generated file will be named "sliceit.py" and located in the
current directory.  
""")

    args = parser.parse_args()

    run(args)

def generate_template(args):
    import os
    target_path = os.getcwd() + "/" + "sliceit.py"
    target_path2 = os.getcwd() + "/" + "slicetimestack.py"

    if os.path.exists(target_path2) or os.path.exists(target_path): #args.gentemplate_name):
        print("Error: Configuration files already exist in the current directory.")
        #raise FileExistsError
        return 1
    else:
        import sampleslicer
        import shutil
        tmpl_path = sampleslicer.__path__[0] + "/template/sliceit.py"
        shutil.copy(tmpl_path, target_path)
        print("Generating new sliceit.py from {}".format(tmpl_path))
        tmpl_path = sampleslicer.__path__[0] + "/template/slicetimestack.py"
        shutil.copy(tmpl_path, target_path2)
        print("Generating new slicetimestack.py from {}".format(tmpl_path))

def run(args):

    num_cmds = int(args.edit) + int(args.batch) + int(args.gen)
    do_run = num_cmds == 1

    if not do_run:
        print("Error: One and only one action must be specified.")
        return 1
        
    if args.batch or args.edit:

        import os
        import importlib

        sliceit_path = os.getcwd() + "/sliceit.py"
        print(("Using configuration script: {}".format(sliceit_path)))

        # import the sliceit module
        spec = importlib.util.spec_from_file_location("sliceit.py", sliceit_path)
        sliceit_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sliceit_mod)

        sliceit_mod.batch_generate = args.batch
        sliceit_mod.run()

    elif args.gen:
        generate_template(args)
    else:
        raise

