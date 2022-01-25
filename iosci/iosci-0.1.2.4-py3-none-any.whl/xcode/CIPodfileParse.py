'''

解析podfile到model对象

podfile有特殊要求：
target end必须成对出现，不支持嵌套

'''
from iosci.Podfile.CIComponentModel import CIComponentModel
from iosci.Util.CIVersionManager import CIVersionManager


class CIPodfileParse(object):

    # 检查podfile是否符合规范，不支持嵌套target
    def checkForPodfile(podfile_lines):
        targetBegin = 0
        for line in podfile_lines:
            podfile_lstrip_line = line.lstrip()
            if podfile_lstrip_line.startswith("target "):
                targetBegin += 1
                if targetBegin >= 2:
                    return False
            if podfile_lstrip_line.startswith("end"):
                targetBegin -= 1
        return True

    '''
    解析podfile中的pod每一行到ComponentModel对象
    '''
    @staticmethod
    def parseForPodLine(line):
        pod_strip_line_segs = line.replace(" ", "").split(',')
        cm = CIComponentModel()
        for segment in pod_strip_line_segs:
            if 'pod\'' in segment:
                cm.name = segment.replace('pod\'', '  pod \'')
            elif ':git' in segment:
                cm.git = segment
            elif ':branch' in segment:
                cm.branch = segment
            elif ':configurations' in segment:
                cm.configurations = segment
            elif CIVersionManager.isVersion(segment.replace('\'', '')):
                cm.version = segment
            else:
                cm.other = segment
        return cm

    '''
    解析podfile中每一行成model对象
    '''
    @staticmethod
    def parseForPodfile(podfile_lines):
        # 是否到target行
        targetBegin = False
        # 是否target下对应的end出来
        outTarget = True
        ret = []
        for podfile_line in podfile_lines:
            podfile_lstrip_line = podfile_line.lstrip()
            # 这些开头的字段，左边如果有空格就全去掉
            if podfile_lstrip_line.startswith("install! ") or \
                    podfile_lstrip_line.startswith("source ") or \
                    podfile_lstrip_line.startswith("target ") or \
                    podfile_lstrip_line.startswith("pod ") or \
                    podfile_lstrip_line.startswith("platform "):
                pass
            elif not podfile_lstrip_line:
                continue
            else:
                podfile_lstrip_line = podfile_line

            if podfile_lstrip_line.startswith("target "):
                targetBegin = True
                outTarget = False
                targetArr = []
            elif podfile_lstrip_line.startswith("end"):
                if targetBegin:
                    targetBegin = False
                    targetArr.append(podfile_lstrip_line + '\n')
            elif not podfile_lstrip_line:  # 空行处理
                continue

            # 已经进入target体，开始解析target内容
            if targetBegin:
                if podfile_lstrip_line.startswith("pod "):
                    cm = CIPodfileParse.parseForPodLine(podfile_lstrip_line)
                    contained = False
                    for pod in targetArr:
                        if isinstance(pod, CIComponentModel) and pod.name == cm.name:
                            contained = True
                            break
                    if not contained:
                        targetArr.append(cm)
                else:
                    targetArr.append(podfile_lstrip_line)
            elif not outTarget:
                outTarget = True
                ret.append(targetArr)
            else:
                ret.append(podfile_lstrip_line)
        return ret

    '''
    传入Podfile文件路径，获取到podfile Model对象
    '''
    @staticmethod
    def getPodfileModel(podfile_path):
        with open(podfile_path, 'r') as podfile:
            _podfile_lines = podfile.readlines()
            if not CIPodfileParse.checkForPodfile(_podfile_lines):
                print("podfile 不符合要求（不能target嵌套）")
                exit(-90)
            podfile_model = CIPodfileParse.parseForPodfile(_podfile_lines)
            return podfile_model
        raise Exception("读取podfile失败")


if __name__ == '__main__':
    podfile = '/Users/lch/Documents/ziroom/proj/ziroom-client-ios/Podfile'
    podfile_model = CIPodfileParse.getPodfileModel(podfile)
    print(podfile_model)