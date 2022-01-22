from RespawnSimulator.utils import debugOut, echo


class Character:
    def __init__(self, name, properties):
        self.Name = name
        self.Properties = properties

    def check_talent(self):  # TODO:check talent
        pass

    def show(self):
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
        if ppt_name in self.Properties:
            self.Properties[ppt_name].add(value)
        else:
            debugOut("Chara_Change", "{0} not found".format(ppt_name))

    def change_max(self, ppt_name, value):
        if ppt_name in self.Properties:
            self.Properties[ppt_name].set_max(value)
        else:
            debugOut("Chara_Change_Max", "{0} not found".format(ppt_name))

    def change_min(self, ppt_name, value):
        if ppt_name in self.Properties:
            self.Properties[ppt_name].set_min(value)
        else:
            debugOut("Chara_Change_Min", "{0} not found".format(ppt_name))

    def get(self, ppt_name):
        if ppt_name in self.Properties:
            return self.Properties[ppt_name].Value
        else:
            debugOut("Chara_Get", "{0} not found".format(ppt_name))
