#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/01/26 16:03
# @Author  : xiong.yuanzhou

import time
import random, uuid
import datetime
from aishu.datafaker.profession.entity import date

class ParaDateFiledServer(object):
    # def __init__(self,info):
    #     self.info = info
    """
    生成接口字段参数
    """

    def getName(self):
        name = str(random.choice(range(10, 999))) + '_' + str(random.choice(range(10, 999)))
        return name

    def getSwClosed(self):
        return 'disable'

    def getSwOpen(self):
        return 'enable'

    def getIp(self):
        ipList = ["192.168.84.105",
                  "192.168.84.192",
                  "192.168.84.217",
                  "192.168.84.108",
                  "192.168.84.107",
                  "192.168.84.182",
                  "192.168.84.193",
                  "192.168.84.109",
                  "192.168.84.175",
                  "192.168.84.60",
                  "192.168.84.61",
                  "192.168.84.63",
                  "192.168.84.62",
                  "192.168.84.64",
                  "192.168.84.65",
                  "192.168.84.66"]
        return random.choice(ipList)

    def getPort(self):
        # 系统合法参数 20010-20099、162，514，5140
        portList = [port for port in range(20010, 20100)]
        portList.append(162)
        portList.append(514)
        portList.append(5140)
        port = random.choice(portList)
        return port

    def getIpVR(self):
        return '{ip1}.{ip2}.{ip3}.{ip4}'.format(ip1=10, ip2=random.choice(range(10, 250)),
                                                ip3=random.choice(range(10, 250)), ip4=random.choice(range(10, 250)))

    def getIpError(self):
        return '{ip1}.{ip2}.{ip3}.{ip4}'.format(ip1='abc', ip2=random.choice(range(10, 99)),
                                                ip3=random.choice(range(10, 99)), ip4=random.choice(range(10, 99)))

    def getUUid(self):
        uuidStr = uuid.uuid4()
        return str(uuidStr)


    def getStartTime(self):
        return int(round(time.time() * 1000))

    def getEndTime(self):
        return int(round(time.time() * 1000))

    def getUpdateTime(self):
        return int(round(time.time()))

    def getEtlPortIll(self):
        portList = [port for port in range(10000, 20000)]
        port = random.choice(portList)
        return port

    def getFromTime(self):
        timeList = []
        differenceTime = 60 * 1000
        ToTime = self.getEndTime()
        timeList.append(ToTime - 12 * 60 * differenceTime)
        timeList.append(ToTime - 24 * 60 * differenceTime)
        startTime = random.choice(timeList)
        date.FromTime_List.append(startTime)
        date.ToTime_List.append(ToTime)
        return startTime

    def getFutureTime(self):
        timeList = []
        differenceTime = 60 * 1000
        ToTime = self.getStartTime()
        timeList.append(ToTime + 24 * 60 * differenceTime)
        FutureTime = random.choice(timeList)
        date.FromTime_List.append(FutureTime)
        date.ToTime_List.append(ToTime)
        return FutureTime

    def getToTime(self):
        return 0 if not date.ToTime_List else date.ToTime_List[0]

    def getUtcStartTime(self):
        year_1 = str(int(time.strftime("%Y", time.localtime())) - 1)
        year_2 = str(int(time.strftime("%Y", time.localtime())) - 2)
        year_3 = str(int(time.strftime("%Y", time.localtime())) - 3)
        year_4 = str(int(time.strftime("%Y", time.localtime())) - 4)
        year_5 = str(int(time.strftime("%Y", time.localtime())) - 5)
        time_list = [year_1, year_2, year_3, year_4, year_5]
        info = {
            'year': random.choice(time_list),
            'month': time.strftime("%m", time.localtime()),
            'day': time.strftime("%d", time.localtime()),
            'hour': time.strftime("%H", time.localtime()),
            'minute': time.strftime("%M", time.localtime()),
            'second': time.strftime("%S", time.localtime()),
        }
        ut_time = info['year'] + '-' + info['month'] + '-' + info['day'] + ' ' + info['hour'] + ':' + info['minute'] + ':' + info['second']
        bj_time = datetime.datetime.strptime(ut_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=8)
        bj_time_info = str(bj_time).split(' ')
        bj_time_year = str(bj_time_info[0]).split('-')
        bj_time_host = str(bj_time_info[1]).split(':')

        return bj_time_year[0] + '-' + bj_time_year[1] + '-' + bj_time_year[2] + 'T' + bj_time_host[0] + ':' + bj_time_host[1] + ':' + bj_time_host[2] + '.000Z'

    def getUtcEndTime(self):
        info = {
            'year': str(int(time.strftime("%Y", time.localtime())) + 1),
            'month': time.strftime("%m", time.localtime()),
            'day': time.strftime("%d", time.localtime()),
            'hour': time.strftime("%H", time.localtime()),
            'minute': time.strftime("%M", time.localtime()),
            'second': time.strftime("%S", time.localtime()),
        }
        ut_time = info['year'] + '-' + info['month'] + '-' + info['day'] + ' ' + info['hour'] + ':' + info['minute'] + ':' + info['second']
        bj_time = datetime.datetime.strptime(ut_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=8)
        bj_time_info = str(bj_time).split(' ')
        bj_time_year = str(bj_time_info[0]).split('-')
        bj_time_host = str(bj_time_info[1]).split(':')
        return bj_time_year[0] + '-' + bj_time_year[1] + '-' + bj_time_year[2] + 'T' + bj_time_host[0] + ':' + bj_time_host[1] + ':' + bj_time_host[2] + '.000Z'

    def getStartDate(self):
        startdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return startdate

    def getEndDate(self):
        enddate = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        return enddate

    def getkpiNameID(self):
        name = str(random.choice(range(10, 999))) + '_' + str(random.choice(range(10, 999)))
        return name

    def kpiNameId(self):
        name = str(random.choice(range(10, 999))) + '_' + str(random.choice(range(10, 999)))
        return name

    def getTimeRangeId(self):
        FromID = 0 if not date.FromTime_List else date.FromTime_List[0]
        ToID = 0 if not date.ToTime_List else date.ToTime_List[0]
        time_diff = ToID - FromID
        time_unit = {
            date.time_diff_value[0]: {
                'timeRange': 30,
                'rangeUnit': 'm',
                'timeLabel': 'last30Minutes'
            },
            date.time_diff_value[1]: {
                'timeRange': 6,
                'rangeUnit': 'h',
                'timeLabel': 'last6Hours'
            },
            date.time_diff_value[2]: {
                'timeRange': 12,
                'rangeUnit': 'h',
                'timeLabel': 'last12Hours'
            },
            date.time_diff_value[3]: {
                'timeRange': 24,
                'rangeUnit': 'h',
                'timeLabel': 'last24Hours'
            }
        }
        time_Info = time_unit[str(time_diff)]
        timeRange_Info = time_Info['timeRange']

        return timeRange_Info

    def getRangeUnitId(self):
        FromID = 0 if not date.FromTime_List else date.FromTime_List[0]
        ToID = 0 if not date.ToTime_List else date.ToTime_List[0]
        time_diff = ToID - FromID
        time_unit = {
            date.time_diff_value[0]: {
                'timeRange': 30,
                'rangeUnit': 'm',
                'timeLabel': 'last30Minutes'
            },
            date.time_diff_value[1]: {
                'timeRange': 6,
                'rangeUnit': 'h',
                'timeLabel': 'last6Hours'
            },
            date.time_diff_value[2]: {
                'timeRange': 12,
                'rangeUnit': 'h',
                'timeLabel': 'last12Hours'
            },
            date.time_diff_value[3]: {
                'timeRange': 24,
                'rangeUnit': 'h',
                'timeLabel': 'last24Hours'
            }
        }
        time_Info = time_unit[str(time_diff)]
        rangeUnit_Info = time_Info['rangeUnit']

        return rangeUnit_Info

    def getTimeLabelId(self):
        FromID = 0 if not date.FromTime_List else date.FromTime_List[0]
        ToID = 0 if not date.ToTime_List else date.ToTime_List[0]
        time_diff = ToID - FromID
        time_unit = {
            date.time_diff_value[0]: {
                'timeRange': 30,
                'rangeUnit': 'm',
                'timeLabel': 'last30Minutes'
            },
            date.time_diff_value[1]: {
                'timeRange': 6,
                'rangeUnit': 'h',
                'timeLabel': 'last6Hours'
            },
            date.time_diff_value[2]: {
                'timeRange': 12,
                'rangeUnit': 'h',
                'timeLabel': 'last12Hours'
            },
            date.time_diff_value[3]: {
                'timeRange': 24,
                'rangeUnit': 'h',
                'timeLabel': 'last24Hours'
            }
        }
        time_Info = time_unit[str(time_diff)]
        timeLabel_Info = time_Info['timeLabel']

        return timeLabel_Info

    def now_time(self):
        now_times = time.strftime("%H:%M", time.localtime())
        return now_times

    def five_feature_time(self):
        five_feature_times = (datetime.datetime.now()+datetime.timedelta(minutes=5)).strftime('%H:%M')
        return five_feature_times