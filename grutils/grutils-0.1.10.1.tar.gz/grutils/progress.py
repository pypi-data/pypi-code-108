#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint
from typing import List, Optional, Dict


class Progress:
    def __init__(self):
        self.curr = 0
        self.max = 10000
        self.progress_bar = None
        self.__root_step_data: Dict = {
            'percent': 1.0,
            'is_finished': False
        }

    def set_process_bar(self, process_bar):
        self.progress_bar = process_bar
        if self.progress_bar is not None:
            self.progress_bar["value"] = self.curr
            self.progress_bar["maximum"] = self.max

    def set(self, val: int):
        if val < 0:
            val = 0

        self.curr = val
        print("[progress] percent:", self.curr_percent())
        if self.progress_bar is not None:
            self.progress_bar["value"] = min(self.curr, self.max)
            self.progress_bar.update()

    def set_percent(self, percent: float):
        self.set(int(percent * self.max))

    def curr_percent(self):
        return float(self.curr) / float(self.max)

    def increase_percent(self, delta_percent: float):
        percent = self.curr_percent() + delta_percent
        self.set_percent(percent)

    def reset(self, unregister_all_steps: bool = False):
        if unregister_all_steps:
            self.__root_step_data = {
                'percent': 1.0,
                'is_finished': False
            }
        else:
            self.__set_step_status(False)
        self.set(0)

    def finish(self):
        self.finish_step()

    def remaining(self):
        return self.max - self.curr

    def remaining_percent(self):
        return 1.0 - self.curr_percent()

    def __find_step(self, chain: Optional[List[str]] = None):
        step_chain: List[Dict] = [self.__root_step_data]

        if chain is None:
            return step_chain

        for step_name in chain:
            father_step = step_chain[-1]
            if 'steps' not in father_step or step_name not in father_step['steps']:
                print('[progress] warning: step {} in chain {} not found'.format(step_name, chain))
                return None

            step_chain.append(father_step['steps'][step_name])

        return step_chain

    def register_step(self, step: str, weight: float, chain: Optional[List[str]] = None):
        step_chain = self.__find_step(chain)
        if step_chain is None:
            return

        father_step = step_chain[-1]
        if 'steps' not in father_step:
            father_step['steps'] = {}
        father_steps = father_step['steps']

        father_steps[step] = {
            'percent': weight,
            'is_finished': False
        }

    def re_assign_steps(self):
        def re_assign_sub_steps(d: Dict):
            if 'steps' not in d:
                return

            d_subs_total_percent = 0.0
            for step in d['steps']:
                d_subs_total_percent += d['steps'][step]['percent']

            if d_subs_total_percent == 0.0:
                return

            for step in d['steps']:
                d_sub = d['steps'][step]
                re_assign_sub_steps(d_sub)
                d_sub['percent'] = round((d_sub['percent'] / d_subs_total_percent) * 100000) / 100000

        re_assign_sub_steps(self.__root_step_data)

    def __set_step_status(self, is_finished: bool, chain: Optional[List[str]] = None):
        def reset_step(d: Dict):
            d['is_finished'] = is_finished
            if 'steps' in d:
                for step in d['steps']:
                    reset_step(d['steps'][step])

        step_chain = self.__find_step(chain)
        if step_chain is not None:
            reset_step(step_chain[-1])
        if is_finished:
            _chain = ["@"] if chain is None else ["@"] + chain
            print('[progress] step: {} finished'.format("=>".join(_chain)))

    def __cal_percent_from_step_data(self):
        def percent_of(d: Dict, d_father_total_percent: float):
            d_total_percent = d_father_total_percent * d['percent']
            if d['is_finished']:
                return d_total_percent

            if 'steps' not in d:
                return 0.0

            d_subs_curr_percent = 0.0
            for step in d['steps']:
                d_subs_curr_percent += percent_of(d['steps'][step], d_total_percent)
            return d_subs_curr_percent

        return percent_of(self.__root_step_data, 1.0)

    def finish_step(self, chain: Optional[List[str]] = None):
        self.__set_step_status(True, chain)

        self.set_percent(self.__cal_percent_from_step_data())

    def dump_steps(self):
        pprint(self.__root_step_data)


shared_progress = Progress()
