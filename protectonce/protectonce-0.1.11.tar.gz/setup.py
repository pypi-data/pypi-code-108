import os
import os.path as path
import shutil
import setuptools


def copy_util():

    base_path = path.dirname(path.abspath(path.join(__file__, "..")))
    remove_dir_list = ["protectonce", "protectonce.egg-info", "dist", "build"]
    for dir in remove_dir_list:
        try:
            shutil.rmtree(path.join(path.abspath(os.getcwd()), dir))
        except OSError as error:
            print(error)

    source = path.join(base_path, "src")
    d1 = path.dirname(path.abspath(path.join(__file__, ".")))
    d2 = path.join(d1, "protectonce")
    try:
        shutil.copytree(source, d2, symlinks=False, ignore=None)

    except shutil.SameFileError:
        print("Source and destination represents the same file.")
    except PermissionError:
        print("Permission denied.")
    except FileNotFoundError:
        print("File not found")
    except FileExistsError:
        print("Folder or files already exists")
    except:
        print("Error occurred while copying file.")
    with open(path.abspath(path.join(__file__, "../protectonce/__init__.py")), "a") as f:
        f.write("from .protect_once import *")


copy_util()


with open("README.md", "r") as fh:
    long_description = fh.read()

# then pass data_files to setup()
setuptools.setup(
    name="protectonce",
    version="0.1.11",
    author="protectonce",
    author_email="protectonce@protectonce.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    description="python agent package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProtectOnce/python_agent.git",
    install_requires=[
        "wrapt==1.13.3",
        "orjson==3.6.4",
        "protectonce-native>=0.1.7",
        "setuptools==60.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
