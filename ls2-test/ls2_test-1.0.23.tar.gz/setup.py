import os
import hashlib
from setuptools import setup, find_packages
from spotii.version import version, status

def calculate_checksum(filenames):
    hash = hashlib.md5()
    for fn in filenames:
        if os.path.isfile(fn):
            hash.update(open(fn, "rb").read())
    return hash.digest()
def md5_for_files(folder):
    files = os.listdir(folder)
    filenames=[]
    #print(os.getcwd())
    for each in files:
        if not each.endswith('.md5'):
            filenames.append(os.path.join(folder,each))
    print(filenames)
    result=calculate_checksum(filenames)

    print(result)
    
    with open(folder+'/'+'chk_sum.md5',"wb") as outfile:
        outfile.write(result)

    with open(folder+'/'+'chk_sum.md5',"rb") as inputfile:
        readBack=inputfile.read()
        print(readBack)
    
md5_for_files(os.path.join(os.getcwd(),'spotii/launcher'))
    
# __packages__ = find_packages(
#     where = 'spotii_project',
# #    include = ['define*',],
# #    exclude = ['additional',]
#     )
#__packages__ = ['spotii'] + __packages__
__packages__=['spotii','spotii.guifolder','spotii.communication','spotii.on_off','spotii.test_handler','spotii.off_line_handler','spotii.language',
              'spotii.guifolder.help_folder','spotii.guifolder.profile_folder','spotii.guifolder.setting_folder',
              'spotii.guifolder.wifi_folder','spotii.guifolder.volume','spotii.guifolder.slot',
              'spotii.guifolder.profile_folder.profile_detail','spotii.guifolder.profile_folder.sign_detail',
              'spotii.guifolder.setting_folder.time_zone','spotii.guifolder.setting_folder.brightness','spotii.guifolder.setting_folder.cassette_type',
              'spotii.language.Arabic','spotii.language.Chinese Traditional','spotii.language.English','spotii.language.French',
              'spotii.language.Indonesian','spotii.language.Japanese','spotii.language.Spanish','spotii.language.Thailand',
              ]
#__packages__=['spotii']
print(__packages__)


# _ROOT = os.path.abspath(os.path.dirname(__file__))
# def get_data(path):
#     return os.path.join(_ROOT, 'data', path)

#print get_data('resource1/foo.txt')
print(version)
if status == 'release':
    package_name = "spotii"
    entry = 'spotii=spotii.__main__:spot_main'
else:
    package_name = "ls2_test"
    entry = 'ls2_test=spotii.__main__:spot_main'
setup(
    name = package_name,
    version = version,
    description = "Look Spot II",
    author = 'Laipac',
    author_email = 'feng.gao@laipac.com',
    url = 'https://github.com/gxfca/gitTest',
    packages = __packages__,
#    package_dir ={'spoitii':'spotii'},
    package_data={
        'spotii':[
                    'guifolder/*.ui',
                    'guifolder/help_folder/*.ui',
                    'guifolder/wifi_folder/*.ui',
                    'guifolder/volume/*.ui',
                    'guifolder/profile_folder/*.ui',
                    'guifolder/slot/*.ui',                    
                    'guifolder/profile_folder/profile_detail/*.ui',
                    'guifolder/profile_folder/sign_detail/*.ui',
                    'guifolder/setting_folder/*.ui',
                    'guifolder/setting_folder/time_zone/*.ui',
                    'guifolder/setting_folder/brightness/*.ui',
                    'guifolder/setting_folder/cassette_type/*.ui',                   
                    'launcher/*',
                    'language/Arabic/*',
                    'language/Chinese Traditional/*',
                    'language/English/*',
                    'language/French/*',
                    'language/Indonesian/*',
                    'language/Japanese/*',
                    'language/Spanish/*',
                    'language/Thailand/*',
                  ],
                  },
    entry_points={
    'console_scripts': [
        entry,
    ],
    },
    )
