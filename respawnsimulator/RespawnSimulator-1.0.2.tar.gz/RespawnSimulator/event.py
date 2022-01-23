import random

from RespawnSimulator.utils import debugOut, echo

MaxBit = 100


class _Event:
    # event_id = [0]

    def __init__(self, eid, name, description, conditions, properties, weight=1, tags=[], repeat=False):
        """
        :param eid: 事件id
        :param name: 事件名
        :param description: 事件描述
        :param conditions: (>=,<) 如果最小值大于最大值，则数值越大概率越低
        :param properties: 事件带来的属性影响
        :param weight: 权重
        :param tags: 事件的标签
        :param repeat: 是否可以重复发生
        :type name: str
        :type description: str
        :type conditions: dict[str,(int,int)]
        :type properties: dict[str,int]
        :type weight: int
        :type tags: list[str]
        :type repeat: bool
        """
        self._Id = eid
        self.Name = name
        self.Weight = weight
        self.Tags = tags
        self.Description = description
        self.Conditions = conditions
        self.Properties = properties
        self.Repeat = repeat
        # self.event_id[0] += 1
        # print(self.event_id[0])

    def eid(self) -> int:
        """
        返回事件id
        """
        return self._Id

    def happen(self, character):
        """
        :param character: 被事件卷入的角色
        :type character: RespawnSimulator.character.Character
        :return: None
        """
        if not self.Repeat:
            self.Weight = 0
        for ppt_name in self.Properties:
            value = self.Properties[ppt_name]
            if type(value) == int:
                character.change(ppt_name, value)
            else:
                character.change(ppt_name, character.get(value))
            if len(ppt_name) >= 1 and ppt_name[0] == "_":
                pass
            else:
                if value > 0:
                    echo("{0} +{1}".format(character.Properties[ppt_name].Name, value))
                else:
                    echo("{0} {1}".format(character.Properties[ppt_name].Name, value))

    def cacl_percent(self, character):
        """
        :param character: 被事件卷入的角色
        :type character: RespawnSimulator.character.Character
        :return: int
        """
        result = 0
        cdt_count = len(self.Conditions)
        if cdt_count <= 0:
            return 0  # 事件没有触发条件，不可能触发
        every_percent = 100 / cdt_count
        for ppt_name in self.Conditions:
            cdt_min = self.Conditions[ppt_name][0]
            cdt_max = self.Conditions[ppt_name][1]
            if cdt_min > cdt_max:
                cdt_min, cdt_max = cdt_max, cdt_min
                cdt_buff = 0
            else:
                cdt_buff = 1
            chara_value = character.Properties[ppt_name].Value
            # if cdt_max - cdt_min <= 0:
            # return 0  # 如果条件最小值小于等于最大值，不可能触发
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


class Events:
    def __init__(self, name, empty_event_name, empty_event_description):
        """
        :param name: 事件组名
        :param empty_event_name: 空事件名
        :param empty_event_description: 空事件描述
        :type name: str
        :type empty_event_name: str
        :type empty_event_description: str
        """
        self.Name = name
        self.events = []
        self._total = 0
        self.append(empty_event_name, empty_event_description, {}, {}, 1, [], True)  # 空事件

    def append(self, name, description, conditions, properties, weight=1, tags=[], repeat=False):
        """
        :param name: 事件名
        :param description: 事件描述
        :param conditions: (min,max) 如果最小值大于最大值，则数值越大概率越低
        :param properties: 事件带来的属性影响
        :param weight: 权重
        :param tags: 事件的标签
        :param repeat: 是否可以重复发生
        :type name: str
        :type description: str
        :type conditions: dict[str,(int,int)]
        :type properties: dict[str,int]
        :type weight: int
        :type tags: list[str]
        :type repeat: bool
        """
        self.events.append(_Event(self._total, name, description, conditions, properties, weight, tags, repeat))
        self._total += 1

    def return_events(self):
        return self.events

    def get_event(self, eid):
        """
        :param eid: 事件id
        :type eid: int
        :return: _Event
        """
        return self.events[eid]

    def happen(self, eid, character):
        """
        :param eid: 事件id
        :param character: 被事件卷入的角色
        :type eid: int
        :type character: RespawnSimulator.character.Character
        :return: None
        """
        self.events[eid].happen(character)

    def set_condition(self, eid, ppt_name, section):
        """
        :param eid: 事件id
        :param ppt_name: 属性名
        :type ppt_name: str
        :param section: 条件元组 e.g. (20,41) 表示事件触发需数值满足 [20,41)
        :type section: (int,int)
        :return:
        """
        if ppt_name in self.events[eid].Conditions:
            self.events[eid].Conditions[ppt_name] = section
        else:
            debugOut("Event_Set_Condition", "{0} not found".format(ppt_name))

    def set_property(self, eid, ppt_name, value):
        """
        :param eid: 事件id
        :param ppt_name: 属性名
        :type ppt_name: str
        :param value: 影响的数值 正数则增加，负数则减少
        :type value: int
        :return:
        """
        if ppt_name in self.events[eid].Properties:
            self.events[eid].Properties[ppt_name].Value = value
        else:
            debugOut("Event_Set_Property", "{0} not found".format(ppt_name))


def GodChoose(character, events: Events) -> int:
    """
    :param character: 被决定命运的角色
    :type character: RespawnSimulator.character.Character
    :param events: 事件组
    :type events: Events
    :return: int 事件id
    """

    def getPercent(elem):
        return elem[1]

    events = events.return_events()
    valid_events = []
    for event in events:
        percent = event.cacl_percent(character)
        if percent > 0:  # 排除不可能发生事件
            valid_events.append((event.eid(), percent, event.Weight))

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
