import random

from RespawnSimulator.utils import debugOut, echo

MaxBit = 100


class Event:
    event_id = [0]

    def __init__(self, name, description, conditions, properties, weight=1, tags=[], repeat=False):
        '''
        :param name:
        :param description:
        :param conditions:
                (>=,<= ,buff)
                >=  大于或等于此值触发
                <=  小于或等于此值触发
        :param properties:
        '''
        self.Id = self.event_id[0]
        self.Name = name
        self.Weight = weight
        self.Tags = tags
        self.Description = description
        self.Conditions = conditions
        self.Properties = properties
        self.Repeat = repeat
        self.event_id[0] += 1
        # print(self.event_id[0])

    def happen(self, character):
        echo("============<<{0}>>============".format(self.Name))  # 发生事件
        echo("  " + self.Description)
        if not self.Repeat:
            self.Weight = 0
        for ppt_name in self.Properties:
            value = self.Properties[ppt_name]
            character.change(ppt_name, value)
            if len(ppt_name) >= 1 and ppt_name[0] == "_":
                pass
            else:
                if value > 0:
                    echo("{0} +{1}".format(character.Properties[ppt_name].Name, value))
                else:
                    echo("{0} {1}".format(character.Properties[ppt_name].Name, value))

    def set_condition(self, ppt_name, section):
        if ppt_name in self.Conditions:
            self.Conditions[ppt_name] = section
        else:
            debugOut("Event_Set_Condition", "{0} not found".format(ppt_name))

    def set_property(self, ppt_name, value):
        if ppt_name in self.Properties:
            self.Properties[ppt_name].Value = value
        else:
            debugOut("Event_Set_Property", "{0} not found".format(ppt_name))

    def cacl_percent(self, character):
        result = 0
        cdt_count = len(self.Conditions)
        if cdt_count <= 0:
            return 0  # 事件没有触发条件，不可能触发
        every_percent = 100 / cdt_count
        for ppt_name in self.Conditions:
            cdt_min = self.Conditions[ppt_name][0]
            cdt_max = self.Conditions[ppt_name][1]
            if len(self.Conditions[ppt_name]) > 2:
                cdt_buff = self.Conditions[ppt_name][2]
            else:
                cdt_buff = 1
            chara_value = character.Properties[ppt_name].Value
            if cdt_max - cdt_min <= 0:
                return 0  # 如果条件最小值小于等于最大值，不可能触发
            if chara_value < cdt_max:
                diff = chara_value - cdt_min
                if diff >= 0:
                    if cdt_buff >= 1:
                        if diff == 0:
                            diff = 1
                        result += every_percent / (cdt_max - cdt_min) * diff  # 计算概率（数值越高，概率越大）
                    else:
                        result += every_percent / (cdt_max - cdt_min) * (cdt_max - chara_value)  # 计算概率（数值越高，概率越小）
                else:
                    # print(self.Name,"角色值小于事件最低值 ",diff)
                    return 0
            else:
                # print("角色值大于事件最大值")
                return 0
        # print(self.Name,result)
        return result


def GodChoose(character, events) -> int:
    def getPercent(elem):
        return elem[1]

    valid_events = []
    for event in events:
        percent = event.cacl_percent(character)
        if percent > 0:  # 排除不可能发生事件
            valid_events.append((event.Id, percent, event.Weight))

    # print(valid_events)
    valid_events.sort(key=getPercent, reverse=True)
    if len(valid_events) <= 0:
        return 0  # 零号空事件
    min_percent = valid_events[-1][1]
    rate = MaxBit / min_percent

    in_groove_events = []
    less_bits = MaxBit
    for item in valid_events:
        bits = int(item[1] / rate * item[2])
        in_groove_events.append((item[0], bits))
        less_bits -= bits
        if less_bits <= 0:
            break
    # print(in_groove_events)
    n = random.randint(0, MaxBit)
    for item in in_groove_events:
        if n < item[1]:
            return item[0]

    return 0  # 没有落在事件槽的有效位，空事件
