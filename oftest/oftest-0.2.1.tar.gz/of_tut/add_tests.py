import os
import glob
from shutil import copyfile

# list_allrun = glob.glob('./*/Allrun')
# print(list_allrun)

def list_files(filepath):
    paths = []
    for root, dirs, files in os.walk(filepath):
      for file in files:
         if file == "Allrun":  #lower().endswith(filetype.lower()):
            paths.append(os.path.join(root, file))
    return paths

allruns = list_files(".")

VALID_DIRS = ["compressible","combustion","discreteMethods","DNS",
              "electromagnetics","finiteArea","heatTransfer","incompressible",
              "lagrangian","multiphase","stressAnalysis",]

test_template = "test_template.py"

for allrun in allruns:

    for v_dir in VALID_DIRS:
        if v_dir in allrun:
            dir_name = os.path.dirname(allrun)
            basename = os.path.basename(dir_name)
            test_filename = "test_" + basename + ".py"
            dst = os.path.join(dir_name,test_filename)
            copyfile(test_template, dst)