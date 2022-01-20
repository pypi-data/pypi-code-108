import numpy as np
from matplotlib.patches import Rectangle


class Rect2D:

    def __str__(self):
        return "left_bottom:" + str(self.points) + ", window_size: (" + str(self.xbox) + ", " + str(self.ybox) + ")"

    def __init__(self, points=(0,0), xbox=1, ybox=1, round_random=False):
        # if points[0] < 0:
        #     points[0] = 0
        # if points[1] < 0:
        #     points[1] = 0
        if xbox < 1:
            xbox = 1
        if ybox < 1:
            ybox = 1
        self.points = (int(points[0]), int(points[1]))
        if round_random:
            if self.__roll(xbox - np.floor(xbox)):
                self.xbox = int(np.ceil(xbox))
            else:
                self.xbox = int(np.floor(xbox))
        if round_random:
            if self.__roll(ybox - np.floor(ybox)):
                self.ybox = int(np.ceil(ybox))
            else:
                self.ybox = int(np.floor(ybox))
        else:
            self.xbox = int(xbox)
            self.ybox = int(ybox)

    def __roll(self, percent=0.5):
        return percent > np.random.rand()

    def squared_rect(self, bound_x_min=0, bound_x_max=-1, bound_y_min=0, bound_y_max=-1):
        box = max(self.xbox, self.ybox)
        center = np.copy(self.center)
        # print(center, box)
        if center[0] - box / 2 < bound_x_min:
            box = (center[0] - bound_x_min) * 2
        if center[1] - box / 2 < bound_y_min:
            box = (center[1] - bound_y_min) * 2
        self.xbox = box
        self.ybox = box
        self.points = int(center[0] - self.xbox / 2), int(center[1] - self.ybox / 2)


    @property
    def center(self):
        return (int(self.points[0] + self.xbox/2), int(self.points[1] + self.ybox/2))

    def extract_2d_map_from_rect(self, map: np.ndarray):
        x_point, y_point = self.points[0], self.points[1]
        return map[y_point:y_point+self.ybox, x_point:x_point+self.xbox]

    def draw_rect_patch_on_matplot(self, ax, c="r"):
        _rect = Rectangle(self.points, self.xbox, self.ybox, linewidth=1, edgecolor=c, facecolor="none")
        ax.add_patch(_rect)

    @staticmethod
    def get_random_rect(data: np.ndarray, x_box_min, x_box_max, y_box_min, y_box_max, fixed_center=None):
        if len(data.shape) != 2:
            raise ValueError("Wrong Data Shape")
        size = (np.random.uniform(low=x_box_min, high=x_box_max, size=1),
                np.random.uniform(low=y_box_min, high=y_box_max, size=1))
        if fixed_center is None:
            points = np.random.uniform(low=0, high=data.shape[0]-size[0]), np.random.uniform(low=0, high=data.shape[1]-size[1])
        else:
            points = fixed_center[0] - size[0]/2, fixed_center[1] - size[1]/2

        return Rect2D(points, size[0], size[1])
