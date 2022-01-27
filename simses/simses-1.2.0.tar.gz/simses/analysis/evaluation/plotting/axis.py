

class Axis:

    def __init__(self, data, label: str, color: str = '#0074D9', linestyle: str = 'solid'):
        self.__data = data
        self.__label = label
        self.__color = color
        self.__linestyle = linestyle

    @property
    def data(self):
        return self.__data

    @property
    def label(self):
        return self.__label

    @property
    def color(self):
        return self.__color

    @property
    def linestyle(self):
        return self.__linestyle