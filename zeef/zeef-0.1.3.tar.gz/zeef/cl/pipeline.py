"""
    Basic pipeline for interactive continual learning.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 15/12/2021
"""


class Pipeline:

    def __init__(self):
        self.loop_round = 0

    def set_round(self, loop_round: int):
        self.loop_round = loop_round

    def run(self):
        pass

    def get_cl_tasks(self):
        pass
