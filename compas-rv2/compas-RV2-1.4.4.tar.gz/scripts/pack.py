import conda_pack
import os
import shutil
import time


import argparse

parser = argparse.ArgumentParser(description='RhinoVault2 release package tool.')
parser.add_argument('--skip_packing', action='store_true', help="skip packaging to dist folder")
parser.add_argument('--version', default="v0.0.0", help="version number")

args = parser.parse_args()

HERE = os.path.dirname(__file__)

if os.path.exists("dist"):
    shutil.rmtree("dist")
os.makedirs("dist/RV2")

start = time.time()
conda_pack.pack(output="dist/env.zip", verbose=True, n_threads=-1, force=True)

print('unpacking to dist/env')
shutil.unpack_archive("dist/env.zip", "dist/RV2/env")

print("copy install.bat")
shutil.copyfile(os.path.join(HERE, "install.bat"), "dist/RV2/install.bat")

print("copy rui")
shutil.copyfile(os.path.join(HERE, "..", "src/compas_rv2/ui/Rhino/RV2/dev/RV2.rui"), "dist/RV2/RV2.rui")

print('removing unnecessary files')
for root, dirs, files in os.walk("dist/RV2/env"):

    for d in dirs:
        if d.find("node_modules") >= 0:
            shutil.rmtree(os.path.join(root, d))

    for f in files:
        if f.find("electron.zip") >= 0:
            os.remove(os.path.join(root, f))


if args.skip_packing:

    print('finished, took %s s' % (time.time()-start))
    print('packing skipped, go to ui/Rhino/RV2/dev and run install.bat(win) or install.command(mac)')

else:

    os.remove("dist/env.zip")
    print('re-packing whole plugin')

    shutil.make_archive(f"dist/RV2_{args.version}", "zip", "dist/RV2")
    shutil.rmtree("dist/RV2")

    print('finished, took %s s' % (time.time()-start))
