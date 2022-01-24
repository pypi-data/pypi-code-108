from RespawnSimulator.utils import debugOut, echo


class Character:
    def __init__(self, name, properties):
        """
        :param name: 角色名
        :param properties: 属性字典 若属性字典名以下划线开头则声明为隐藏属性 e.g. _age
        :type name: str
        :type properties: dict[str,RespawnSimulator.property.Property]
        """
        self.Name = name
        self.Properties = properties

    def check_talent(self):  # TODO:check talent
        pass

    def show(self):
        """
        显示角色属性 不显示隐藏属性 以下划线开头的属性字典名为隐藏属性
        """
        for ppt_name in self.Properties:
            if len(ppt_name) >= 1:
                if ppt_name[0] == "_":
                    continue
            if self.Properties[ppt_name].Value == self.Properties[ppt_name].Max:
                echo("{0}: {1}".format(self.Properties[ppt_name].Name, "MAX"))
            elif self.Properties[ppt_name].Value == self.Properties[ppt_name].Min:
                echo("{0}: {1}".format(self.Properties[ppt_name].Name, "MIN"))
            else:
                echo("{0}: {1}".format(self.Properties[ppt_name].Name, self.Properties[ppt_name].Value))

    def change(self, ppt_name, value):
        """
        :param ppt_name: 属性名
        :param value: 变化的数值 正数为增加，负数为减少
        :type ppt_name: str
        :type value: int
        :return: None
        """
        if ppt_name in self.Properties:
            self.Properties[ppt_name].add(value)
        else:
            debugOut("Chara_Change", "{0} not found".format(ppt_name))

    def change_max(self, ppt_name, value):
        """
        :param ppt_name: 属性名
        :param value: 设置的最大值
        :type ppt_name: str
        :type value: int
        :return: None
        """
        if ppt_name in self.Properties:
            self.Properties[ppt_name].set_max(value)
        else:
            debugOut("Chara_Change_Max", "{0} not found".format(ppt_name))

    def change_min(self, ppt_name, value):
        """
        :param ppt_name: 属性名
        :param value: 设置的最小值
        :type ppt_name: str
        :type value: int
        :return: None
        """
        if ppt_name in self.Properties:
            self.Properties[ppt_name].set_min(value)
        else:
            debugOut("Chara_Change_Min", "{0} not found".format(ppt_name))

    def get(self, ppt_name):
        """
        :param ppt_name: 属性名
        :type ppt_name: str
        :return: None
        """
        if ppt_name in self.Properties:
            return self.Properties[ppt_name].Value
        else:
            debugOut("Chara_Get", "{0} not found".format(ppt_name))
