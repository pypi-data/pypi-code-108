from typing import Dict


class DataLayout:
    def __init__(self, batch_axis: int):
        self.batch_axis = batch_axis

    def add_axis(self, name: str, axis: int) -> None:
        setattr(self, name, axis)

    def dump(self) -> Dict[str, int]:
        data = self.__dict__
        del data["dump"]
        del data["add_axis"]
        return data


class ImageDataLayout(DataLayout):
    def __init__(self, batch_axis: int, channel_axis: int,
                 hight_axis: int, width_axis: int) -> None:
        self.batch_axis = batch_axis
        self.channel_axis = channel_axis
        self.hight_axis = hight_axis
        self.width_axis = width_axis
