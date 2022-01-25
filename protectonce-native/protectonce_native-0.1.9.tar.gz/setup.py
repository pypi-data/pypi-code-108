import setuptools
import shutil
import os
import os.path as path


def copy_util():
    base_path = path.dirname(path.abspath(path.join(__file__, "..")))
    remove_dir_list = ['protectonce_native',
                       'protectonce_native.egg-info', 'dist', 'build']
    for dir in remove_dir_list:
        try:
            shutil.rmtree(path.join(path.abspath(os.getcwd()), dir))
        except OSError as error:
            print(error)
    try:
        os.mkdir(path.join(path.abspath(os.getcwd()), 'protectonce_native'))
    except FileExistsError:
        print("folder already exists")

    packaging_dir_list = ['lib/libnode.so', 'out', 'runtimes', 'agent_core/node_modules', 'agent_core/lib',
                          'agent_core/index.js', 'agent_core/package.json', 'agent_core/package-lock.json']
    try:
        for dir in packaging_dir_list:
            source = path.join(base_path, dir)
            d1 = path.dirname(path.abspath(path.join(__file__, ".")))
            d2 = path.join(d1, 'protectonce_native/{}'.format(dir))
            if path.isfile(source):
                if not path.exists(d2.rpartition('/')[0]):
                    os.makedirs(d2.rpartition('/')[0])
                shutil.copy(source, d2.rpartition('/')[0])
            else:
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
    try:
        os.rename("protectonce_native/agent_core", "protectonce_native/core")
    except:
        print('already renamed')

    if path.exists('__init__.py'):
        print('__init__.py file exists')
    else:
        try:
            with open(path.join(d1, 'protectonce_native/__init__.py'), 'wb') as temp_file:
                temp_file.close()
                print('__init__.py file created')
        except os.error:
            print("Error creating file")


copy_util()
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='protectonce_native',
    version='0.1.9',
    author="protectonce",
    author_email="protectonce@protectonce.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    description="python agent interface native package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProtectOnce/agent_interface.git",
    classifiers=[
        "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
    ]
)
