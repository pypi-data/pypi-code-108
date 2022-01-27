import os
from .path_dir import find_file_name_path_list
def remove_all_files_by_name(path:str,name:str)->int:
    '''输入名字，返回删除文件个数'''
    flist = find_file_name_path_list(path,name)
    for fi in flist:
        os.remove(fi)
        return len(flist)






# # 自动写一个python
# # 例如
# LiOH_path = ''
# package_description ={
#     "name"         : "LiOH",
#     "version"      : "0.1.11",
#     "description"  : "A LiOH package",
#     "author"       : "LiOH",
#     "author_email" : "908716811@qq.com",
#     "url"          : "http://www.LiOH.xyz/",
#     "packages"     : ['LiOH', 'LiOH.adv']
# }
# with open(LiOH_path+'test_version.py','w') as f:
#     contents = 'package_description = {\n '+',\n'.join(str(package_description).split(','))[1:]
#     f.write(contents)