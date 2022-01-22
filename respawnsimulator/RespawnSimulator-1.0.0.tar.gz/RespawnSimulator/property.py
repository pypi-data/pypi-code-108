class Property:
    def __init__(self, name, default=0, min_value=0, max_value=100):
        self.Name = name
        self.Min = min_value
        self.Max = max_value
        self.Value = default
        self.InitValue = default

    def add(self, value):
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
        if value > self.Max:
            self.Value = self.Max
        elif value < self.Min:
            self.Value = self.Min
        else:
            self.Value = value

    def set_max(self, value):
        self.Max = value
        if self.Max < self.Min:
            self.Min = self.Max
        self.set(self.Value)

    def set_min(self, value):
        self.Min = value
        if value > self.Max:
            self.Max = self.Min
        self.set(self.Value)


def test():
    health=Property("health",0,100,100)
    print(health.Value)
    health.add(10)
    print(health.Value)
    health.add(-10)
    print(health.Value)
    health.set(1000)
    print(health.Value)
    health.set_max(50)
    print(health.Value)
    health.set_min(60)
    print(health.Value)
if __name__ =="__main__":
    test()
