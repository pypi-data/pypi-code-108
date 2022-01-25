import inspect
import random

from RespawnSimulator.utils import debugOut, echo


class _Event:
    # event_id = [0]

    def __init__(self, eid, name, description, conditions, properties, weight=1, tags=[], repeat=False, rise="{0} +{1}",
                 decline="{0} -{1}"):
        """
        :param eid: 事件id
        :param name: 事件名
        :param description: 事件描述
        :param conditions: (>=,<) 如果最小值大于最大值，则数值越大概率越低
        :param properties: 事件带来的属性影响
        :param weight: 权重
        :param tags: 事件的标签
        :param repeat: 是否可以重复发生
        :param rise: 事件发生，数值上升提示文本，0为属性名，1为变化的数值。e.g. "{0} 上升了{1}点！"
        :param decline: 事件发生，数值下降提示文本，0为属性名，1为变化的数值。e.g. "{0} 下降了{1}点！"
        :type eid: int
        :type name: str
        :type description: str
        :type conditions: dict[str,(int,int)]
        :type properties: dict[str,int]
        :type weight: int
        :type tags: list[str]
        :type repeat: bool
        :type rise: str
        :type decline: str
        """
        self._Id = eid
        self.Name = name
        self.Weight = weight
        self.Tags = tags
        self.Description = description
        self.Conditions = conditions
        self.Properties = properties
        self.Repeat = repeat
        self.Rise = rise
        self.Decline = decline
        # self.event_id[0] += 1
        # print(self.event_id[0])

    def eid(self) -> int:
        """
        返回事件id
        """
        return self._Id

    def get(self, value_name):
        """
        :param value_name: 要获取的事件参数 name,description,conditions,properties等
        :type value_name: str
        """
        vn = value_name[0].upper() + value_name[1:]
        if vn in self.__dict__:
            return self.__dict__[vn]
        else:
            debugOut("EVENT_GET_ERR", value_name + " doesn't exist.")
            return None

    def set(self, name=None, description=None, conditions=None, properties=None, weight=None, tags=None,
            repeat=None, rise=None, decline=None):
        """
        :param name: 事件名
        :param description: 事件描述
        :param conditions: (>=,<) 如果最小值大于最大值，则数值越大概率越低
        :param properties: 事件带来的属性影响
        :param weight: 权重
        :param tags: 事件的标签
        :param repeat: 是否可以重复发生
        :param rise: 事件发生，数值上升提示文本，0为属性名，1为变化的数值。e.g. "{0} 上升了{1}点！"
        :param decline: 事件发生，数值下降提示文本，0为属性名，1为变化的数值。e.g. "{0} 下降了{1}点！"
        :type name: str
        :type description: str
        :type conditions: dict[str,(int,int)]
        :type properties: dict[str,int]
        :type weight: int
        :type tags: list[str]
        :type repeat: bool
        :type rise: str
        :type decline: str
        """
        value_map = locals()
        for param in inspect.getfullargspec(self.set).args[1:]:
            if value_map[param] is not None:
                self.__dict__[param[0].upper() + param[1:]] = value_map[param]

    def happen(self, character):
        """
        :param character: 被事件卷入的角色
        :type character: RespawnSimulator.character.Character
        :return: None
        """
        if not self.Repeat:
            self.Weight = 0
        if type(self.Properties) == dict:
            ppts = self.Properties
        else:
            debugOut("EVENT_HAPPEN_ERR", "Properties type:" + str(type(self.Properties)))
            ppts = {}
        for ppt_name in ppts:
            value = ppts[ppt_name]
            if type(value) == int:
                character.change(ppt_name, value)
            else:
                character.change(ppt_name, character.get(value))
            if len(ppt_name) >= 1 and ppt_name[0] == "_":
                pass
            else:
                if value > 0:
                    echo(self.Rise.format(character.Properties[ppt_name].Name, value))
                else:
                    echo(self.Decline.format(character.Properties[ppt_name].Name, 0 - value))

    def cacl_percent(self, character):
        """
        :param character: 被事件卷入的角色
        :type character: RespawnSimulator.character.Character
        :return: int
        """
        if self._Id == 0:
            return 0
        if character is None:
            return 100
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
    def __init__(self, name, empty_event_name, empty_event_description, empty_event_properties={},
                 default_rise="{0} +{1}",
                 default_decline="{0} -{1}"):
        """
        :param name: 事件组名
        :param empty_event_name: 空事件名
        :param empty_event_description: 空事件描述
        :param empty_event_properties: 空事件影响属性
        :param default_rise: 当组内事件未设置数值上升提示文本时的默认文本
        :param default_decline: 当组内事件未设置数值下降提示文本时的默认文本
        :type name: str
        :type empty_event_name: str
        :type empty_event_description: str
        :type empty_event_properties: dict[str,int]
        :type default_rise: str
        :type default_decline: str
        """
        self.Name = name
        self._events = []
        self._total = 0
        self.Default_rise = default_rise
        self.Default_decline = default_decline
        self.append(empty_event_name, empty_event_description, {}, empty_event_properties, 1, [], True, default_rise,
                    default_decline)  # 空事件

    def append(self, name, description, conditions, properties, weight=1, tags=[], repeat=False, rise=None,
               decline=None):
        """
        :param name: 事件名
        :param description: 事件描述
        :param conditions: (min,max) 如果最小值大于最大值，则数值越大概率越低
        :param properties: 事件带来的属性影响
        :param weight: 权重
        :param tags: 事件的标签
        :param repeat: 是否可以重复发生
        :param rise: 事件发生，数值上升提示文本，0为属性名，1为变化的数值。e.g. "{0} 上升了{1}点！"
        :param decline: 事件发生，数值下降提示文本，0为属性名，1为变化的数值。e.g. "{0} 下降了{1}点！"
        :type name: str
        :type description: str
        :type conditions: dict[str,(int,int)]
        :type properties: dict[str,int]
        :type weight: int
        :type tags: list[str]
        :type repeat: bool
        :type rise: str
        :type decline: str
        """
        if rise is None:
            rise = self.Default_rise
        if decline is None:
            decline = self.Default_decline
        self._events.append(
            _Event(self._total, name, description, conditions, properties, weight, tags, repeat, rise, decline))
        self._total += 1

    def return_events(self):
        return self._events

    def get_event(self, eid):
        """
        :param eid: 事件id
        :type eid: int
        :return: _Event
        """
        if eid < len(self._events):
            return self._events[eid]
        else:
            debugOut("Events_Get_Event", "Eid error " + str(eid))
            return None

    def __add__(self, other):
        if type(other) == Events:
            for event in other.return_events()[1:]:
                self.append(event.Name, event.Description, event.Conditions, event.Properties, event.Weight, event.Tags,
                            event.Repeat, event.Rise, event.Decline)
        else:
            debugOut("EVENTS_ADD_ERR", str(type(other)))
        return self

    def get(self, eid, value_name):
        """
        :param eid: 事件id
        :param value_name: 要获取的事件参数 name,description,conditions,properties等
        :type value_name: str
        :type eid: int
        """
        return self.get_event(eid).get(value_name)

    def set(self, eid, name=None, description=None, conditions=None, properties=None, weight=None, tags=None,
            repeat=None, rise=None, decline=None):
        """
        :param eid: 事件id
        :param name: 事件名
        :param description: 事件描述
        :param conditions: (>=,<) 如果最小值大于最大值，则数值越大概率越低
        :param properties: 事件带来的属性影响
        :param weight: 权重
        :param tags: 事件的标签
        :param repeat: 是否可以重复发生
        :param rise: 事件发生，数值上升提示文本，0为属性名，1为变化的数值。e.g. "{0} 上升了{1}点！"
        :param decline: 事件发生，数值下降提示文本，0为属性名，1为变化的数值。e.g. "{0} 下降了{1}点！"
        :type eid: int
        :type name: str
        :type description: str
        :type conditions: dict[str,(int,int)]
        :type properties: dict[str,int]
        :type weight: int
        :type tags: list[str]
        :type repeat: bool
        :type rise: str
        :type decline: str
        """
        self.get_event(eid).set(name, description, conditions, properties, weight, tags,
                                repeat, rise, decline)

    def happen(self, eid, character):
        """
        :param eid: 事件id
        :param character: 被事件卷入的角色
        :type eid: int
        :type character: RespawnSimulator.character.Character
        :return: None
        """
        self.get_event(eid).happen(character)

    def set_condition(self, eid, ppt_name, section):
        """
        :param eid: 事件id
        :param ppt_name: 属性名
        :type ppt_name: str
        :param section: 条件元组 e.g. (20,41) 表示事件触发需数值满足 [20,41)
        :type section: (int,int)
        :return:
        """
        ev = self.get_event(eid)
        if ppt_name in ev.Conditions:
            ev.Conditions[ppt_name] = section
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
        ev = self.get_event(eid)
        if ppt_name in ev.Properties:
            ev.Properties[ppt_name].Value = value
        else:
            debugOut("Event_Set_Property", "{0} not found".format(ppt_name))

    def god_choose(self, character=None, no_space=False, density=None) -> int:
        """
        :param character: 被决定命运的角色，若不提供角色则所有事件视为完全达到发生条件（除空事件)
        :type character: RespawnSimulator.character.Character
        :param no_space: 若有事件可发生则一定不为空事件（除非没有事件可发生）
        :type no_space: bool
        :param density: 事件发生密度，默认为最密，数值仅能为负数，即减小密度。
        :type density: int
        :return: int 事件id
        """

        def getPercent(elem):
            return elem[1]

        # events = events.return_events()
        valid_events = []
        for event in self._events:
            percent = event.cacl_percent(character)
            if percent > 0:  # 排除不可能发生事件
                valid_events.append((event.eid(), percent, event.Weight))

        # print(valid_events)
        valid_events.sort(key=getPercent, reverse=True)
        if len(valid_events) <= 0:
            return 0  # 零号空事件

        # rate = density / min_percent

        in_groove_events = []
        fill_bits = 0
        min_percent = valid_events[-1][1]
        for item in valid_events:
            bits = int(item[1] / min_percent * item[2])
            if bits <= 0:
                continue
            fill_bits += bits
            in_groove_events.append((item[0], fill_bits))

        if density is None or density >= 0:
            density = self._total - 1
        else:
            density = self._total - density - 1

        if fill_bits > density:
            density = fill_bits

        if no_space:
            n = random.randint(0, in_groove_events[-1][1] - 1)
        else:
            n = random.randint(0, density)
        for item in in_groove_events:
            if n < item[1]:
                return item[0]

        return 0
