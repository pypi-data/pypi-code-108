


"""
搜集插件各个类
"""


class Plugin(object):


    def __init__(self):

        # 插件的３个组件
        self.connection = {}
        self.actions = {}
        self.triggers = {}
        self.indicator_receivers = {}
        self.alarm_receivers = {}


    def add_connection(self, connect):
        self.connection[connect.name] = connect

    def add_actions(self, action):
        self.actions[action.name] = action

    def add_triggers(self, trigger):
        self.triggers[trigger.name] = trigger

    def add_indicator_receivers(self, indicator_receiver):
        self.indicator_receivers[indicator_receiver.name] = indicator_receiver
    
    def add_alarm_receivers(self, alarm_receiver):
        self.alarm_receivers[alarm_receiver.name] = alarm_receiver


