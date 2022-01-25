class Property:
    def __init__(self, name, default=0, min_value=0, max_value=100):
        """
        :param name: 属性名
        :param default: 默认数值
        :param min_value: 最小值
        :param max_value: 最大值
        :type name: str
        :type default: int
        :type min_value: int
        :type max_value: int
        """
        self.Name = name
        self.Min = min_value
        self.Max = max_value
        self.Value = default
        self.InitValue = default

    def add(self, value):
        """
        :param value: 变化数值 正数为增加，负数为减少
        :type value: int
        :return: None
        """
        if value > 0:
            if self.Value + value >= self.Max:
                self.Value = self.Max
            else:
                self.Value += value
        else:
            if self.Value + value <= self.Min:
                self.Value = self.Min
            else:
                self.Value += value

    def set(self, value):
        """
        :param value: 设置数值
        :type value: int
        :return: None
        """
        if value > self.Max:
            self.Value = self.Max
        elif value < self.Min:
            self.Value = self.Min
        else:
            self.Value = value

    def set_max(self, value):
        """
        :param value: 设置的最大值
        :type value: int
        :return: None
        """
        self.Max = value
        if self.Max < self.Min:
            self.Min = self.Max
        self.set(self.Value)

    def set_min(self, value):
        """
        :param value: 设置的最小值
        :type value: int
        :return: None
        """
        self.Min = value
        if value > self.Max:
            self.Max = self.Min
        self.set(self.Value)

