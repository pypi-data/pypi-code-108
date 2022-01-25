
import os.path
import shutil
from git import Repo

#
#
# # 将单个组件的git地址+branch 改为path指向
# def update_component_gitbranch2path_model(component_name, source_path, podfile_model):
#     # 找出第一个target
#     first_target = []
#     # 组件在podfile中存在，更新版本号
#     for target in podfile_model:
#         if isinstance(target, list):
#             if len(first_target) == 0:
#                 first_target = target
#
#             for component in target:
#                 if isinstance(component, ComponentModel) and component.name == component_name:
#                     component.version = ''
#                     component.git = ''
#                     if component.other:
#                         if not ':path' in component.other:
#                             component.other = f":path=> '{source_path}', " + component.other
#                     else:
#                         component.other = f":path=> '{source_path}'"
#                     break
#
#
# def modify_podfile_git2path(f_podfile, component_source_root_path):
#     # 路径不存在则先创建
#     if not os.path.exists(component_source_root_path):
#         os.mkdir(component_source_root_path)
#
#     # 读取podfile文件，翻译为对象
#     podfile_model = getPodfileModel(f_podfile)
#     for target in podfile_model:
#         if isinstance(target, list):
#             for component in target:
#                 if isinstance(component, ComponentModel):
#                     if component.git:
#                         component_raw_name = component.name.replace(' ','')
#                         component_name =  component_raw_name.replace('pod\'','').replace('\'','')
#                         # 拉取代码到component_source_root_path
#                         to_path = os.path.join(component_source_root_path, component_name)
#
#                         if os.path.exists(to_path):
#                             print(f"路径 {to_path} 已经存在")
#                             should_force = input("是否覆盖？（如果有修改，覆盖后将无法找回）！y：覆盖 n:停止执行 j：跳过这个组件")
#                             if should_force.lower() == 'y':
#                                 shutil.rmtree(to_path, ignore_errors=True)
#                             elif should_force.lower() == 'n':
#                                 exit(0)
#                             else:
#                                 continue
#
#                         giturl = component.git.replace(":git=>","").replace('\'','')
#                         branch = component.branch.replace(":branch=>","").replace('\'','').replace("\n",'')
#                         Repo.clone_from(giturl, to_path=to_path, branch=branch)
#
#                         # 把path地址修改到podfile_model中
#                         update_component_gitbranch2path_model(component.name, to_path, podfile_model)
#
#     print(podfile_model)
#     # 把传过来的组件更新到对象中
#     # for component in components:
#     #     update_component_gitbranch2path_model(component, "'%s'" % component_source_root_path, podfile_model)
#     # else:
#     #     raise Exception("传过来的组件格式不对 %s" % component)
#     #
#     # # 把新的内容写入到podfile中
#     # rewrite_to_podfile(f_podfile, podfile_model)
#
# # 工程中执行pod update,返回podfile lock文件路径
# def podupdate(project_dir):
#     try:
#         update_cmd = 'cd %s; pod update --repo-update > /dev/null 2>&1' % project_dir
#         os_system(update_cmd)
#         return os.path.join(project_dir, 'Podfile.lock')
#     except Exception as e:
#         raise e
#
# if __name__ == '__main__':
#     f_podfile = '/Users/lch/Desktop/Podfile'
    # f_podfile = '/Users/lch/Documents/ziroom/proj/Podfile'
    # update_component_with_newversion(f_podfile, ['aaa:1.0.1', 'bbb:2.0'])

    # 修改podfile git地址指向本地path
    # 传podfile和root目录，root目录是组件源码父目录，比如 /Users/a/Desktop/component/YYModel, root目录是/Users/a/Desktop/component
    # modify_podfile_git2path(f_podfile, '/Users/lch/Documents/ziroom/proj/component/hehe')
