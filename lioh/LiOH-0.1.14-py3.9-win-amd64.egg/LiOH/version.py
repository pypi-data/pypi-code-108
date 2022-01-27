# 版本信息
package_description ={
    "name"         : "LiOH",
    "version"      : "0.1.14",
    "description"  : "A LiOH package",
    "author"       : "LiOH",
    "author_email" : "908716811@qq.com",
    "url"          : "http://www.LiOH.xyz/",
}
from .file import all_dir_file_paths
import platform
packages = ['LiOH']
if platform.system()=='Windows':
    LiOH_path = '\\'.join(__file__.split('\\')[:-1])
    packages.extend([i[len(LiOH_path)-4:].replace('\\','.') for i in all_dir_file_paths(LiOH_path)[0] if i.split('\\')[-1]!='__pycache__'])
else:
    LiOH_path = '/'.join(__file__.split('/')[:-1])
    packages.extend([i[len(LiOH_path)-4:].replace('/','.') for i in all_dir_file_paths(LiOH_path)[0] if i.split('/')[-1]!='__pycache__'])
package_description['packages'] = packages