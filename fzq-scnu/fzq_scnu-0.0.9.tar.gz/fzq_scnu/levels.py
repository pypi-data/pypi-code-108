# coding=<encoding name> ： # coding=utf-8
from fzq_scnu.constants import elements as e


class Level:  # 默认展示背景
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels']['默认']  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []  # 特殊物品


class Level0:  # 空白背景
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][0]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors'][0]  # 角色
        self.others = []  # 特殊物品


# --------------------------------------------------------------------------------------------------------
# 所有关卡的虚拟场景，及其参数
class Level1:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][1]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors'][1]  # 角色
        self.others = []  # 特殊物品


class Level2:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][2]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors'][2]  # 角色
        # self.others = [e['others'][1], e['others'][2]]  # 特殊物品
        self.others = []


class Level3:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][3]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors'][3]  # 角色
        self.others = []


class Level4:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][4]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []


class Level5:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][5]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []

class Level6:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][6]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []


class Level7:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][7]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []


class Level8:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][8]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []


class Level9:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][9]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []


class Level10:
    def __init__(self):
        self.interface = e['interfaces'][1]  # 界面
        self.level = e['levels'][10]  # 场景
        self.racetrack = e['racetracks'][0]  # 赛道
        self.actor = e['actors']['默认']  # 角色
        self.others = []