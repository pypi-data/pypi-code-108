import setuptools
import os
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

# ###############################################
pack_name="eisenradio"
pack_version="0.0.4"
pack_description="Play radio. Record radio. Style your App."

if sys.platform=='win32':
    print('----> sys.platform ' + sys.platform)
    INSTALL_REQUIRES = [
            'setuptools',
            'flask_cors',
            'wmi',
            'pywin32',
            'winshell',
            'winreg',
            'configparser',
            'requests',
            'urllib3'
        ]
else:
    INSTALL_REQUIRES = [
        'setuptools',
        'flask_cors',
        'configparser',
        'requests',
        'urllib3'
    ]
PYTHON_REQUIRES = '>=3.6'


setuptools.setup(

    name=pack_name, # project name /folder
    version=pack_version,
    author="René Horn",
    author_email="rene_horn@gmx.net",
    description=pack_description,
    long_description=long_description,
    license='gpl-3.0',
    long_description_content_type="text/markdown",
    url="",
    include_package_data=True,
    packages=setuptools.find_packages(),
        install_requires=INSTALL_REQUIRES,
    classifiers=[
    # How mature is this project? Common values are
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
    ],
    python_requires=PYTHON_REQUIRES,
)
# https://stackoverflow.com/questions/20288711/post-install-script-with-python-setuptools
# from setuptools import setup
def _post_install():
    import site
    import getpass
    import datetime

    module_dir=''
    print('----------------------------- POST INSTALL ----------------------------------')
    username=getpass.getuser()
    print(os.path.dirname(os.path.abspath(__file__)))
    print('sitepack ' + site.getusersitepackages())

    setup_dir=os.path.dirname(os.path.abspath(__file__))
    for path in sys.path:
        if not path.find(pack_name + '-' + pack_version)==-1:
            if not path==setup_dir:
                module_dir=path + '\\' + pack_name
                print('Module directory: ' + module_dir)

    if sys.platform=='win32':
        print('----> sys.platform ' + sys.platform)
        from win32com.client import Dispatch
        import winreg
        shell = Dispatch('WScript.Shell')
        # Read location of Windows desktop folder from registry
        regName = 'Desktop'
        regPath = r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
        desktopFolder = os.path.normpath(get_reg(regName,regPath))
        print('desktop ' + desktopFolder)

        # Path to location of link file
        link_name = pack_name + '.lnk'
        pathLink = os.path.join(desktopFolder, link_name)
        if os.path.exists(pathLink):
            print("Remove existing shortcut at %s" % repr(pathLink))
            os.unlink(pathLink)

        shortcut = shell.CreateShortCut(pathLink)
        print(pathLink)
        shortcut.WorkingDirectory = module_dir
        shortcut.Targetpath = module_dir + '\\app.py'
        print(module_dir + '\\app.py')
        print(module_dir + '\\eisenradio\\static\\images\\eisen.ico')
        shortcut.IconLocation = module_dir + '\\eisenradio\\static\\images\\eisen.ico'
        shortcut.save()

def get_reg(name,path):
    # Read variable from Windows Registry
    # From https://stackoverflow.com/a/35286642
    import winreg
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

def modules_directory(mod):
    if os.path.exists(mod):
        return mod
	
_post_install()