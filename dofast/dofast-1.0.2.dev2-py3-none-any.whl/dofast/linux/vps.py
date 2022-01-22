#!/usr/bin/env python
import json
import subprocess
import sys
import time
from typing import List, Set, Tuple

import arrow
import codefast as cf
import requests

from dofast.toolkits.telegram import Channel
from dofast.vendor.graphviz import Record


class Time:
    @classmethod
    def get_time(cls) -> dict:
        _time = requests.get(
            "http://worldtimeapi.org/api/timezone/Asia/Shanghai").json()
        cf.info(f"Time: {_time}")
        return _time

    @classmethod
    def get_hour_minute(cls):
        _time = arrow.get(cls.get_time()['datetime']).format('HH-mm')
        cf.info(f'get hour minute returns {_time}')
        return _time

    @classmethod
    def get_date(cls):
        date = arrow.get(cls.get_time()['datetime']).format('YY-MM-DD')
        return date


class VPS:
    def __init__(self,
                 init_day: int = 1,
                 interface: str = 'eth0',
                 vps_name: str = 'vps') -> None:
        self.init_day = int(init_day)
        self.interface = interface
        self.name = vps_name

    @property
    def ip(self) -> str:
        return requests.get('http://ip.42.pl/raw').text

    def vnstat_(self) -> List[Tuple[str]]:
        js = subprocess.check_output('vnstat --json d', shell=True).decode()
        js = json.loads(js)
        bit_shift: int = 20
        daykey: str = 'days'
        interface_key: str = 'id'
        if js['vnstatversion'].startswith('2.'):
            bit_shift = 30
            daykey = 'day'
            interface_key = 'name'

        js = next(
            (e
             for e in js['interfaces'] if e[interface_key] == self.interface),
            {})
        if not js:
            return ''
        daily = js['traffic'][daykey]
        daily.sort(key=lambda d: int(
            d['date']['year']) * 10000 + int(d['date']['month']) * 100 + int(d['date']['day']), reverse=True)

        _id = next((i for i, e in enumerate(daily)
                    if e['date']['day'] == self.init_day),
                   len(daily) - 1)
        rx = sum(e['rx'] for e in daily[:_id + 1]) / (1 << bit_shift)
        tx = sum(e['tx'] for e in daily[:_id + 1]) / (1 << bit_shift)
        previous = (daily[0]['rx'] + daily[0]['tx']) / (1 << bit_shift)
        total = rx + tx
        avg = total / max(_id, 1)
        return [('TX', tx), ('RX', rx), ('TOTAL', total), ('AVG', avg), ('YEST', previous)]

    def vnstat(self) -> str:
        aggre = self.vnstat_()
        return '\n'.join(['{}: {:.2f} GB'.format(k, v) for k, v in aggre])

    def __repr__(self) -> str:
        aggr = [('name', self.name), ('ip', self.ip),
                ('init_day', self.init_day)]
        return '\n'.join(['{}: {}'.format(k, v) for k, v in aggr])

    def info(self) -> List[Tuple[str]]:
        '''return information on VPS with formatted data'''
        __info = [('IP', self.ip), ('Name', self.name),
                  ('Init_Day', self.init_day)]
        __vnstat = self.vnstat_()
        __vnstat = [(e[0], str(round(e[1], 2)) + ' GB') for e in __vnstat]
        aggr = __info + __vnstat + [('Date', Time.get_date())]
        return aggr


class Monitor:
    def __init__(self, vps: VPS, task_types: List[str]) -> None:
        self.task_types = task_types
        self.vps = vps
        self.record = Record(background_color='lightblue')

    def post_telegram(self, text: str) -> None:
        Channel('messalert').post(text)

    def post_telegram_image(self, record_image_path: str) -> None:
        Channel('messalert').post_image(record_image_path, 'VPS status')

    @cf.utils.retry(3, 5)
    def run(self) -> None:
        vps_info = self.vps.info()
        msg = '\n'.join(['{} 〰️ {}'.format(a, b) for a, b in vps_info])
        self.post_telegram(msg)


class Context:
    def parse_args(self) -> dict:
        dct = {}
        pre: str
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                pre = arg.replace('-', '')
                dct[pre] = []
            else:
                dct[pre].append(arg)
        return dct

    def get_first_arg(self, args: dict, key: str, default: str) -> str:
        if key in args:
            return args[key][0]
        return default

    def run(self):
        args = self.parse_args()
        vps_name = self.get_first_arg(args, 'vps_name', 'vps')
        alert_time = self.get_first_arg(args, 'alert_time', '08-01')
        interface = self.get_first_arg(args, 'interface', 'eth0')
        init_day = self.get_first_arg(args, 'init_day', 1)
        vps = VPS(init_day=init_day, vps_name=vps_name, interface=interface)
        monitor = Monitor(vps, task_types=args.get('task_types', []))

        while True:
            if Time.get_hour_minute() == alert_time:
                monitor.run()
                time.sleep(60)
            time.sleep(10)


def main():
    Context().run()
