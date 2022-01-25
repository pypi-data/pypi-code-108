# -*- coding: utf-8 -*-
# @Time     : 2021/9/1 15:15
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : geometry.py
# @Version  : Python 3.8.5 +

def get_circle_by_triangle(_3points: list) -> 'Circle':
    """
    Three points to define a circle
    :param _3points:
    :return: center x, y, R square
    """

    a_x, a_y = _3points[0]
    b_x, b_y = _3points[1]
    c_x, c_y = _3points[2]

    dx_ab = a_x - b_x
    dy_ab = a_y - b_y
    dx_ac = a_x - c_x
    dy_ac = a_y - c_y

    s_a = a_x ** 2 + a_y ** 2
    s_b = b_x ** 2 + b_y ** 2
    s_c = c_x ** 2 + c_y ** 2

    # 3 points on the same line will lead to the value to be 0
    temp = dx_ab * dy_ac - dx_ac * dy_ab

    D = ((s_b - s_a) * dy_ac - (s_c - s_a) * dy_ab) / temp

    if dy_ac == 0:
        E = (s_b - s_a - D * dx_ab) / dy_ab
    else:
        E = (s_c - s_a - D * dx_ac) / dy_ac

    R_sq = (a_x + D/2) ** 2 + (a_y + E/2) ** 2

    center = (-D/2, -E/2)

    return Circle(center, R_sq)


def get_circle_by_2points(_2points: list) -> 'Circle':
    """
    Get a circle given two points
    :param _2points:
    :return: center x, y, R square
    """
    a_x, a_y = _2points[0]
    b_x, b_y = _2points[1]

    center = ((a_x + b_x) / 2, (a_y + b_y) / 2)
    R_sq = ((a_x - b_x) / 2) ** 2 + ((a_y - b_y) / 2) ** 2

    return Circle(center, R_sq)


class Circle:
    def __init__(self, center: tuple, radius_sq: float):

        self.center_x, self.center_y = center
        self.radius_sq = radius_sq

        # print(self.center_x, self.center_y, self.radius_sq)

    def cover(self, point: tuple) -> bool:
        x, y = point
        if self.radius_sq >= (x - self.center_x) ** 2 + (y - self.center_y) ** 2:
            return True
        else:
            return False


class EnclosingCircle(Circle):
    def __init__(self, start_point: tuple):
        super().__init__(start_point, 0)

        self.points_list = [start_point]

    def feed(self, point: tuple):
        self.points_list.append(point)
        # Only 2 points
        if len(self.points_list) == 2:
            circle_temp = get_circle_by_2points(self.points_list)
            self.center_x = circle_temp.center_x
            self.center_y = circle_temp.center_y
            self.radius_sq = circle_temp.radius_sq
            return

        # New point incoming
        else:
            # If the circle has covered the point, ignore this point
            if self.cover(point):
                return
            else:
                new_circle = Circle(point, 0)
                for i in range(len(self.points_list) - 1):
                    if not new_circle.cover(self.points_list[i]):
                        new_circle = get_circle_by_2points([point, self.points_list[i]])
                        for j in range(i):
                            if not new_circle.cover(self.points_list[j]):
                                new_circle = get_circle_by_triangle([point, self.points_list[i], self.points_list[j]])

            self.center_x = new_circle.center_x
            self.center_y = new_circle.center_y
            self.radius_sq = new_circle.radius_sq
        pass
