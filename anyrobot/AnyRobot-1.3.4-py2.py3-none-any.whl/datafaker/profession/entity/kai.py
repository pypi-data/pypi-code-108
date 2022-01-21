import requests
from aishu.public.db_select import select
from aishu import setting

class machine(object):
    def __init__(self, search):
        self.search = search

    def inquireServiceKpi(self):
        serviceKpi = []

        if not (self.search):
            return False

        for key in self.search:
            sql = 'SELECT serviceId,id From KAIKpi where KAIKpi.serviceId={serverID}'.format(serverID=key)
            date = select(sql)
            for sqlDate in date:
                serviceKpi.append(list(sqlDate))
        #当没有查询找数据时，返回错误
        if not (serviceKpi):
            return False

        context = [
            {"key": serviceKpi[0], "operator": "matches", "value": ["2", "0", "3", "4", "5", "6"], "type": "kpi"},
            {"key": serviceKpi[1], "operator": "matches", "value": ["0", "2", "3", "4", "5", "6"], "type": "kpi"},
            {"key": serviceKpi[2], "operator": "matches", "value": ["2", "0", "3", "4", "5", "6"], "type": "kpi"}
        ]
        return context

    def inquireEntity(self):
        entityhostIps = []

        if not (self.search):
            return False

        for key in self.search:
            sql = 'SELECT fieldsCondition From KAIEntity where id={EntityId}'.format(EntityId=key)
            sqldata = select(sql)
            for key in sqldata:
                for entityRules in key:
                    entityRules = eval(entityRules)
                    for entityRule  in entityRules:
                        entityhostIps.append(entityRule['value'])
        #当没有查询找数据时，返回错误
        if not (entityhostIps):
            return False
        data = [{"fieldsCondition": [{"host": {"matches": entityhostIps}}]}]
        return data

    def inquireBusinessKPIAndServiceId(self):
        id=[]
        if not (self.search):
            return False

        for key in self.search:
            sql = 'SELECT serviceId,id From KAIKpi where KAIKpi.serviceId={serverID}'.format(serverID=key)
            sqldata = select(sql)
            for i in sqldata:
                id.append(list(i))
        if not (id):
            return False
        data = [{"id":id[0][1],"type":"kpi"},{"id":id[0][0],"type":"service"}]
        return data

    def ServiceBusiness(self):
        nameAndId=[]
        if not (self.search):
            return False

        for key in self.search:
            sql='SELECT KAIKpi.`name`,KAIKpi.id,KAIService.`name`,KAIKpi.serviceId FROM KAIService INNER JOIN KAIKpi ON KAIService.id = KAIKpi.serviceId WHERE KAIService.id = {serverID}'.format(serverID=key)
            sqldata = select(sql)
            for info in sqldata:

                nameAndId=list(info)
        if not (nameAndId):
            return False

        data = [
            {
                "type": 0,
                "rect": {
                    "x": 442,
                    "y": 265.5,
                    "width": 70,
                    "height": 100,
                    "center": {
                        "x": 477,
                        "y": 315.5
                    },
                    "ex": 512,
                    "ey": 365.5
                },
                "lineWidth": 1,
                "rotate": 0,
                "offsetRotate": 0,
                "globalAlpha": 1,
                "dash": 0,
                "strokeStyle": "#000000",
                "font": {
                    "color": "#000000",
                    "fontFamily": "\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial",
                    "fontSize": 12,
                    "lineHeight": 1.5,
                    "fontStyle": "normal",
                    "fontWeight": "normal",
                    "textAlign": "center",
                    "textBaseline": "middle",
                    "background": ""
                },
                "animateCycleIndex": 0,
                "events": [],
                "eventFns": [
                    "link",
                    "doAnimate",
                    "doFn",
                    "doWindowFn"
                ],
                "id": "ab82928",
                "name": "people",
                "tags": [],
                "lineDashOffset": 0,
                "textOffsetX": 0,
                "textOffsetY": 0,
                "animateType": "",
                "visible": True,
                "data": "",
                "zRotate": 0,
                "anchors": [
                    {
                        "x": 442,
                        "y": 315.5,
                        "direction": 4
                    },
                    {
                        "x": 477,
                        "y": 265.5,
                        "direction": 1
                    },
                    {
                        "x": 512,
                        "y": 315.5,
                        "direction": 2
                    },
                    {
                        "x": 477,
                        "y": 365.5,
                        "direction": 3
                    }
                ],
                "rotatedAnchors": [
                    {
                        "x": 442,
                        "y": 315.5,
                        "direction": 4
                    },
                    {
                        "x": 477,
                        "y": 265.5,
                        "direction": 1
                    },
                    {
                        "x": 512,
                        "y": 315.5,
                        "direction": 2
                    },
                    {
                        "x": 477,
                        "y": 365.5,
                        "direction": 3
                    }
                ],
                "animateDuration": 0,
                "animateFrames": [],
                "z": None,
                "borderRadius": 0,
                "iconSize": 0,
                "imageAlign": "center",
                "gradientAngle": 0,
                "gradientRadius": 0.01,
                "paddingTop": 0,
                "paddingBottom": 0,
                "paddingLeft": 0,
                "paddingRight": 0,
                "paddingLeftNum": 0,
                "paddingRightNum": 0,
                "paddingTopNum": 0,
                "paddingBottomNum": 0,
                "textRect": {
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "center": {
                        "x": 0,
                        "y": 0
                    },
                    "ex": 0,
                    "ey": 0
                },
                "fullTextRect": {
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "center": {
                        "x": 0,
                        "y": 0
                    },
                    "ex": 0,
                    "ey": 0
                },
                "iconRect": {
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "center": {
                        "x": 0,
                        "y": 0
                    },
                    "ex": 0,
                    "ey": 0
                },
                "elementRendered": False,
                "TID": "ec085cd",
                "lastImage": None,
                "dockWatchers": [
                    {
                        "x": 477,
                        "y": 315.5
                    },
                    {
                        "x": 0,
                        "y": 276.5
                    },
                    {
                        "x": 70,
                        "y": 276.5
                    },
                    {
                        "x": 70,
                        "y": 376.5
                    },
                    {
                        "x": 0,
                        "y": 376.5
                    }
                ]
            },
            {
                "type": 0,
                "rect": {
                    "x": 622,
                    "y": 210,
                    "width": 200,
                    "height": 80,
                    "center": {
                        "x": 722,
                        "y": 250
                    },
                    "ex": 822,
                    "ey": 290
                },
                "lineWidth": 1,
                "rotate": 0,
                "offsetRotate": 0,
                "globalAlpha": 1,
                "dash": 0,
                "strokeStyle": "transparent",
                "fillStyle": "#ffffff",
                "font": {
                    "color": "#000000",
                    "fontFamily": "\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial",
                    "fontSize": 12,
                    "lineHeight": 1.5,
                    "fontStyle": "normal",
                    "fontWeight": "normal",
                    "textAlign": "center",
                    "textBaseline": "middle"
                },
                "animateCycleIndex": 0,
                "events": [],
                "eventFns": [
                    "link",
                    "doAnimate",
                    "doFn",
                    "doWindowFn"
                ],
                "id": "531cfaa9",
                "name": "echarts",
                "tags": [],
                "lineDashOffset": 0,
                "textOffsetX": 0,
                "textOffsetY": 0,
                "animateType": "",
                "hideInput": True,
                "visible": True,
                "data": {
                    "text": "{serviceName}_服务健康分数".format(serviceName=nameAndId[2]),
                    "echarts": {
                        "option": {
                            "title": {
                                "text": "服务健康分数",
                                "subtext": "",
                                "left": "center",
                                "top": "bottom",
                                "textStyle": {
                                    "fontFamily": "Microsoft YaHei",
                                    "fontSize": 12,
                                    "fontWeight": "normal",
                                    "color": "#000000",
                                    "lineHeight": 12,
                                    "rich": {
                                        "e": {
                                            "color": "red"
                                        }
                                    }
                                },
                                "subtextStyle": {
                                    "fontSize": 12,
                                    "color": "red"
                                }
                            },
                            "tooltip": {
                                "trigger": "axis",
                                "padding": [
                                    8,
                                    12
                                ]
                            },
                            "grid": [
                                {
                                    "left": 2,
                                    "right": "32.3%",
                                    "borderColor": "transparent",
                                    "top": 2,
                                    "bottom": 24,
                                    "backgroundColor": "#ffe1a8",
                                    "show": True
                                },
                                {
                                    "left": 2,
                                    "right": "33%",
                                    "bottom": 24,
                                    "backgroundColor": "transparent",
                                    "borderColor": "transparent",
                                    "show": True
                                },
                                {
                                    "x": "68%",
                                    "right": 2,
                                    "left": "68%",
                                    "top": 2,
                                    "bottom": 24,
                                    "backgroundColor": "#ffe1a8",
                                    "borderColor": "transparent",
                                    "show": True
                                }
                            ],
                            "xAxis": [
                                {
                                    "gridIndex": 0,
                                    "type": "category",
                                    "data": [
                                        1610935980000,
                                        1610936100000,
                                        1610936220000
                                    ],
                                    "show": False
                                },
                                {
                                    "show": False
                                }
                            ],
                            "yAxis": [
                                {
                                    "gridIndex": 0,
                                    "type": "value",
                                    "show": False
                                },
                                {
                                    "show": False
                                }
                            ],
                            "series": [
                                {
                                    "animation": False,
                                    "hoverAnimation": False,
                                    "data": [
                                        70,
                                        70,
                                        70
                                    ],
                                    "smooth": True,
                                    "showSymbol": True,
                                    "yAxisIndex": 0,
                                    "symbol": "none",
                                    "xAxisIndex": 0,
                                    "symbolSize": 0,
                                    "type": "line",
                                    "lineStyle": {
                                        "color": "#000000"
                                    },
                                    "itemStyle": {
                                        "color": "#000000"
                                    }
                                },
                                {
                                    "tooltip": {
                                        "trigger": "item",
                                        "formatter": "70",
                                        "padding": [
                                            8,
                                            12
                                        ],
                                        "position": [
                                            "80%",
                                            "-50%"
                                        ]
                                    },
                                    "color": "#000000",
                                    "animation": False,
                                    "avoidLabelOverlap": True,
                                    "hoverAnimation": False,
                                    "data": [
                                        {
                                            "value": 100,
                                            "name": "--"
                                        }
                                    ],
                                    "name": "",
                                    "radius": [
                                        "46%",
                                        "46%"
                                    ],
                                    "label": {
                                        "show": True,
                                        "position": "center",
                                        "fontSize": 20,
                                        "formatter": "70",
                                        "rich": {
                                            "n": {
                                                "fontSize": 12
                                            }
                                        }
                                    },
                                    "center": [
                                        "83%",
                                        "44%"
                                    ],
                                    "type": "pie"
                                }
                            ],
                            "severity": [
                                3,
                                3,
                                3
                            ],
                            "type": "service"
                        },
                        "rect": {
                            "width": 200,
                            "height": 80
                        }
                    },
                    "data": {
                        "dataName": "{serviceName}_服务健康分数".format(serviceName=nameAndId[2]),
                        "id": nameAndId[3],
                        "isNotFound": False,
                        "parentId": "{serviceId}".format(serviceId=nameAndId[3]),
                        "type": "service"
                    }
                },
                "zRotate": 0,
                "anchors": [
                    {
                        "x": 622,
                        "y": 250,
                        "direction": 4
                    },
                    {
                        "x": 722,
                        "y": 210,
                        "direction": 1
                    },
                    {
                        "x": 822,
                        "y": 250,
                        "direction": 2
                    },
                    {
                        "x": 722,
                        "y": 290,
                        "direction": 3
                    }
                ],
                "rotatedAnchors": [
                    {
                        "x": 622,
                        "y": 250,
                        "direction": 4
                    },
                    {
                        "x": 722,
                        "y": 210,
                        "direction": 1
                    },
                    {
                        "x": 822,
                        "y": 250,
                        "direction": 2
                    },
                    {
                        "x": 722,
                        "y": 290,
                        "direction": 3
                    }
                ],
                "animateDuration": 0,
                "animateFrames": [],
                "borderRadius": 0,
                "iconSize": None,
                "imageAlign": "center",
                "gradientAngle": 0,
                "gradientRadius": 0.01,
                "paddingTop": 0,
                "paddingBottom": 0,
                "paddingLeft": 0,
                "paddingRight": 0,
                "elementId": "e406b09",
                "paddingLeftNum": 0,
                "paddingRightNum": 0,
                "paddingTopNum": 0,
                "paddingBottomNum": 0,
                "textRect": {
                    "x": 622,
                    "y": 270,
                    "width": 200,
                    "height": 20,
                    "center": {
                        "x": 722,
                        "y": 280
                    },
                    "ex": 822,
                    "ey": 290
                },
                "fullTextRect": {
                    "x": 622,
                    "y": 210,
                    "width": 200,
                    "height": 80,
                    "center": {
                        "x": 722,
                        "y": 250
                    },
                    "ex": 822,
                    "ey": 290
                },
                "iconRect": {
                    "x": 622,
                    "y": 210,
                    "width": 200,
                    "height": 60,
                    "center": {
                        "x": 722,
                        "y": 240
                    },
                    "ex": 822,
                    "ey": 270
                },
                "fullIconRect": {
                    "x": 622,
                    "y": 210,
                    "width": 200,
                    "height": 80,
                    "center": {
                        "x": 722,
                        "y": 250
                    },
                    "ex": 822,
                    "ey": 290
                },
                "elementRendered": True,
                "TID": "ec085cd",
                "elementLoaded": True,
                "dockWatchers": [
                    {
                        "x": 722,
                        "y": 250
                    },
                    {
                        "x": 622,
                        "y": 210
                    },
                    {
                        "x": 822,
                        "y": 210
                    },
                    {
                        "x": 822,
                        "y": 290
                    },
                    {
                        "x": 622,
                        "y": 290
                    }
                ]
            },
            {
                "type": 0,
                "rect": {
                    "x": 622,
                    "y": 336.5,
                    "width": 200,
                    "height": 80,
                    "center": {
                        "x": 722,
                        "y": 376.5
                    },
                    "ex": 822,
                    "ey": 416.5
                },
                "lineWidth": 1,
                "rotate": 0,
                "offsetRotate": 0,
                "globalAlpha": 1,
                "dash": 0,
                "strokeStyle": "transparent",
                "fillStyle": "#ffffff",
                "font": {
                    "color": "#000000",
                    "fontFamily": "\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial",
                    "fontSize": 12,
                    "lineHeight": 1.5,
                    "fontStyle": "normal",
                    "fontWeight": "normal",
                    "textAlign": "center",
                    "textBaseline": "middle"
                },
                "animateCycleIndex": 0,
                "events": [],
                "eventFns": [
                    "link",
                    "doAnimate",
                    "doFn",
                    "doWindowFn"
                ],
                "id": "83348a3",
                "name": "echarts",
                "tags": [],
                "lineDashOffset": 0,
                "textOffsetX": 0,
                "textOffsetY": 0,
                "animateType": "",
                "hideInput": True,
                "visible": True,
                "data": {
                    "text": "{serviceName}_{KPIName}".format(serviceName=nameAndId[2],KPIName=nameAndId[0]),
                    "echarts": {
                        "option": {
                            "title": {
                                "text": "{KPIName}".format(KPIName=nameAndId[0]),
                                "subtext": "",
                                "left": "center",
                                "top": "bottom",
                                "textStyle": {
                                    "fontFamily": "Microsoft YaHei",
                                    "fontSize": 12,
                                    "fontWeight": "normal",
                                    "color": "#000000",
                                    "lineHeight": 12,
                                    "rich": {
                                        "e": {
                                            "color": "red"
                                        }
                                    }
                                },
                                "subtextStyle": {
                                    "fontSize": 12,
                                    "color": "red"
                                }
                            },
                            "tooltip": {
                                "trigger": "axis",
                                "padding": [
                                    8,
                                    12
                                ]
                            },
                            "grid": [
                                {
                                    "left": 2,
                                    "right": "32.3%",
                                    "borderColor": "transparent",
                                    "top": 2,
                                    "bottom": 24,
                                    "backgroundColor": "#ffe1a8",
                                    "show": True
                                },
                                {
                                    "left": 2,
                                    "right": "33%",
                                    "bottom": 24,
                                    "backgroundColor": "transparent",
                                    "borderColor": "transparent",
                                    "show": True
                                },
                                {
                                    "x": "68%",
                                    "right": 2,
                                    "left": "68%",
                                    "top": 2,
                                    "bottom": 24,
                                    "backgroundColor": "#ffe1a8",
                                    "borderColor": "transparent",
                                    "show": True
                                }
                            ],
                            "xAxis": [
                                {
                                    "gridIndex": 0,
                                    "type": "category",
                                    "data": [
                                        1610935980000,
                                        1610936100000,
                                        1610936220000
                                    ],
                                    "show": False
                                },
                                {
                                    "show": False
                                }
                            ],
                            "yAxis": [
                                {
                                    "gridIndex": 0,
                                    "type": "value",
                                    "show": False
                                },
                                {
                                    "show": False
                                }
                            ],
                            "series": [
                                {
                                    "animation": False,
                                    "hoverAnimation": False,
                                    "data": [
                                        345,
                                        355,
                                        383
                                    ],
                                    "smooth": True,
                                    "showSymbol": True,
                                    "yAxisIndex": 0,
                                    "symbol": "none",
                                    "xAxisIndex": 0,
                                    "symbolSize": 0,
                                    "type": "line",
                                    "lineStyle": {
                                        "color": "#000000"
                                    },
                                    "itemStyle": {
                                        "color": "#000000"
                                    }
                                },
                                {
                                    "tooltip": {
                                        "trigger": "item",
                                        "formatter": "383条",
                                        "padding": [
                                            8,
                                            12
                                        ],
                                        "position": [
                                            "80%",
                                            "-50%"
                                        ]
                                    },
                                    "color": "#000000",
                                    "animation": False,
                                    "avoidLabelOverlap": True,
                                    "hoverAnimation": False,
                                    "data": [
                                        {
                                            "value": 100,
                                            "name": "--"
                                        }
                                    ],
                                    "name": "",
                                    "radius": [
                                        "46%",
                                        "46%"
                                    ],
                                    "label": {
                                        "show": True,
                                        "position": "center",
                                        "fontSize": 20,
                                        "formatter": "38...",
                                        "rich": {
                                            "n": {
                                                "fontSize": 12
                                            }
                                        }
                                    },
                                    "center": [
                                        "83%",
                                        "44%"
                                    ],
                                    "type": "pie"
                                }
                            ],
                            "severity": [
                                3,
                                3,
                                3
                            ],
                            "type": "kpi"
                        },
                        "rect": {
                            "width": 200,
                            "height": 80
                        }
                    },
                    "data": {
                        "dataName": "{serviceName}_{KPIName}".format(serviceName=nameAndId[2],KPIName=nameAndId[0]),
                        "id": nameAndId[1],
                        "isNotFound": False,
                        "parentId": "{serviceId}".format(serviceId=nameAndId[3]),
                        "type": "kpi"
                    }
                },
                "zRotate": 0,
                "anchors": [
                    {
                        "x": 622,
                        "y": 376.5,
                        "direction": 4
                    },
                    {
                        "x": 722,
                        "y": 336.5,
                        "direction": 1
                    },
                    {
                        "x": 822,
                        "y": 376.5,
                        "direction": 2
                    },
                    {
                        "x": 722,
                        "y": 416.5,
                        "direction": 3
                    }
                ],
                "rotatedAnchors": [
                    {
                        "x": 622,
                        "y": 376.5,
                        "direction": 4
                    },
                    {
                        "x": 722,
                        "y": 336.5,
                        "direction": 1
                    },
                    {
                        "x": 822,
                        "y": 376.5,
                        "direction": 2
                    },
                    {
                        "x": 722,
                        "y": 416.5,
                        "direction": 3
                    }
                ],
                "animateDuration": 0,
                "animateFrames": [],
                "borderRadius": 0,
                "iconSize": None,
                "imageAlign": "center",
                "gradientAngle": 0,
                "gradientRadius": 0.01,
                "paddingTop": 0,
                "paddingBottom": 0,
                "paddingLeft": 0,
                "paddingRight": 0,
                "elementId": "58cbaa",
                "paddingLeftNum": 0,
                "paddingRightNum": 0,
                "paddingTopNum": 0,
                "paddingBottomNum": 0,
                "textRect": {
                    "x": 622,
                    "y": 396.5,
                    "width": 200,
                    "height": 20,
                    "center": {
                        "x": 722,
                        "y": 406.5
                    },
                    "ex": 822,
                    "ey": 416.5
                },
                "fullTextRect": {
                    "x": 622,
                    "y": 336.5,
                    "width": 200,
                    "height": 80,
                    "center": {
                        "x": 722,
                        "y": 376.5
                    },
                    "ex": 822,
                    "ey": 416.5
                },
                "iconRect": {
                    "x": 622,
                    "y": 336.5,
                    "width": 200,
                    "height": 60,
                    "center": {
                        "x": 722,
                        "y": 366.5
                    },
                    "ex": 822,
                    "ey": 396.5
                },
                "fullIconRect": {
                    "x": 622,
                    "y": 336.5,
                    "width": 200,
                    "height": 80,
                    "center": {
                        "x": 722,
                        "y": 376.5
                    },
                    "ex": 822,
                    "ey": 416.5
                },
                "elementRendered": True,
                "TID": "ec085cd",
                "elementLoaded": True,
                "dockWatchers": [
                    {
                        "x": 722,
                        "y": 376.5
                    },
                    {
                        "x": 622,
                        "y": 336.5
                    },
                    {
                        "x": 822,
                        "y": 336.5
                    },
                    {
                        "x": 822,
                        "y": 416.5
                    },
                    {
                        "x": 622,
                        "y": 416.5
                    }
                ]
            },
            {
                "type": 1,
                "rect": {
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "center": {
                        "x": 0,
                        "y": 0
                    },
                    "ex": 0,
                    "ey": 0
                },
                "lineWidth": 1,
                "rotate": 0,
                "offsetRotate": 0,
                "globalAlpha": 1,
                "dash": 0,
                "strokeStyle": "#000000",
                "fillStyle": "",
                "font": {
                    "color": "",
                    "fontFamily": "\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial",
                    "fontSize": 12,
                    "lineHeight": 1.5,
                    "fontStyle": "normal",
                    "fontWeight": "normal",
                    "textAlign": "center",
                    "textBaseline": "middle",
                    "background": "#fff"
                },
                "animateCycleIndex": 0,
                "events": [],
                "eventFns": [
                    "link",
                    "doAnimate",
                    "doFn",
                    "doWindowFn"
                ],
                "id": "d561b63",
                "name": "curve",
                "tags": [],
                "lineDashOffset": 0,
                "textOffsetX": 0,
                "textOffsetY": 0,
                "visible": True,
                "data": "",
                "controlPoints": [
                    {
                        "x": 592,
                        "y": 315.5,
                        "direction": 2,
                        "anchorIndex": 2,
                        "id": "ab82928"
                    },
                    {
                        "x": 542,
                        "y": 250,
                        "direction": 4,
                        "anchorIndex": 0,
                        "id": "531cfaa9"
                    }
                ],
                "fromArrowSize": 5,
                "toArrowSize": 5,
                "borderWidth": 0,
                "borderColor": "#000000",
                "animateColor": "",
                "animateSpan": 1,
                "animatePos": 0,
                "isAnimate": False,
                "animateFromSize": 0,
                "animateToSize": 0,
                "animateDotSize": 3,
                "from": {
                    "x": 512,
                    "y": 315.5,
                    "direction": 2,
                    "anchorIndex": 2,
                    "id": "ab82928"
                },
                "to": {
                    "x": 622,
                    "y": 250,
                    "direction": 4,
                    "anchorIndex": 0,
                    "id": "531cfaa9"
                },
                "fromArrow": "",
                "toArrow": "triangleSolid",
                "textRect": None,
                "TID": "ec085cd"
            },
            {
                "type": 1,
                "rect": {
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "center": {
                        "x": 0,
                        "y": 0
                    },
                    "ex": 0,
                    "ey": 0
                },
                "lineWidth": 1,
                "rotate": 0,
                "offsetRotate": 0,
                "globalAlpha": 1,
                "dash": 0,
                "strokeStyle": "#000000",
                "fillStyle": "",
                "font": {
                    "color": "",
                    "fontFamily": "\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial",
                    "fontSize": 12,
                    "lineHeight": 1.5,
                    "fontStyle": "normal",
                    "fontWeight": "normal",
                    "textAlign": "center",
                    "textBaseline": "middle",
                    "background": "#fff"
                },
                "animateCycleIndex": 0,
                "events": [],
                "eventFns": [
                    "link",
                    "doAnimate",
                    "doFn",
                    "doWindowFn"
                ],
                "id": "730113e",
                "name": "curve",
                "tags": [],
                "lineDashOffset": 0,
                "textOffsetX": 0,
                "textOffsetY": 0,
                "visible": True,
                "data": "",
                "controlPoints": [
                    {
                        "x": 592,
                        "y": 315.5,
                        "direction": 2,
                        "anchorIndex": 2,
                        "id": "ab82928"
                    },
                    {
                        "x": 542,
                        "y": 376.5,
                        "direction": 4,
                        "anchorIndex": 0,
                        "id": "83348a3"
                    }
                ],
                "fromArrowSize": 5,
                "toArrowSize": 5,
                "borderWidth": 0,
                "borderColor": "#000000",
                "animateColor": "",
                "animateSpan": 1,
                "animatePos": 0,
                "isAnimate": False,
                "animateFromSize": 0,
                "animateToSize": 0,
                "animateDotSize": 3,
                "from": {
                    "x": 512,
                    "y": 315.5,
                    "direction": 2,
                    "anchorIndex": 2,
                    "id": "ab82928"
                },
                "to": {
                    "x": 622,
                    "y": 376.5,
                    "direction": 4,
                    "anchorIndex": 0,
                    "id": "83348a3"
                },
                "fromArrow": "",
                "toArrow": "triangleSolid",
                "textRect": None,
                "TID": "ec085cd"
            }
        ]

        return data

    def inquirePens(self):
        nameAndId=[]
        if not (self.search):
            return False

        for key in self.search:
            sql='SELECT KAIKpi.`name`,KAIKpi.id,KAIService.`name`,KAIKpi.serviceId FROM KAIService INNER JOIN KAIKpi ON KAIService.id = KAIKpi.serviceId WHERE KAIService.id = {serverID}'.format(serverID=key)
            sqldata = select(sql)
            for info in sqldata:

                nameAndId=list(info)
        if not (nameAndId):
            return False

        data=[
            {"type":0, "rect":{"x":546,"y":268,"width":582,"height":117,"center":{"x":837,"y":326.5},"ex":1128,"ey":385}, "lineWidth":1, "rotate":0, "offsetRotate":0,"globalAlpha":1,"dash":0,"strokeStyle":"transparent","fillStyle":"#ffffff", "font":{"color":"#000000","fontFamily":"\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial","fontSize":12,"lineHeight":1.5,"fontStyle":"normal","fontWeight":"normal","textAlign":"center","textBaseline":"middle"}, "animateCycleIndex":0,"events":[],"eventFns":["link","doAnimate","doFn","doWindowFn"],"id":"d0c90c4","name":"echarts","tags":[],"lineDashOffset":0,"textOffsetX":0,"textOffsetY":0,"animateType":"","hideInput":True,"visible":True,
            "data":{"text":"{serviceName}_{KPIName}".format(serviceName=nameAndId[2],KPIName=nameAndId[0]),"echarts":{"option":{"title":{"text":"KPI251_606","subtext":"","left":"center","top":"bottom","textStyle":{"fontFamily":"Microsoft YaHei","fontSize":12,"fontWeight":"normal","color":"#000000","lineHeight":12,"rich":{"e":{"color":"red"}}},"subtextStyle":{"fontSize":12,"color":"red"}},"tooltip":{"trigger":"axis","padding":[8,12]},"grid":[{"left":2,"right":"32.3%","borderColor":"transparent","top":2,"bottom":24,"backgroundColor":"rgba(0, 0, 0, 0.15)","show":True},{"left":2,"right":"33%","bottom":24,"backgroundColor":"transparent","borderColor":"transparent","show":True},{"x":"68%","right":2,"left":"68%","top":2,"bottom":24,"backgroundColor":"rgba(0, 0, 0, 0.15)","borderColor":"transparent","show":True}],"xAxis":[{"gridIndex":0,"type":"category","data":[],"show":False},{"show":False}],"yAxis":[{"gridIndex":0,"type":"value","show":False},{"show":False}],"series":[{"animation":False,"hoverAnimation":False,"data":[],"smooth":True,"showSymbol":True,"yAxisIndex":0,"symbol":"none","xAxisIndex":0,"symbolSize":0,"type":"line","lineStyle":{"color":"#000000"},"itemStyle":{"color":"#000000"}},{"tooltip":{"trigger":"item","formatter":"N/A条","padding":[8,12],"position":["80%","-50%"]},"color":"#000000","animation":False,"avoidLabelOverlap":True,"hoverAnimation":False,"data":[{"value":100,"name":"--"}],"name":"","radius":["46%","46%"],"label":{"show":True,"position":"center","fontSize":20,"formatter":"N/A条","rich":{"n":{"fontSize":12}}},"center":["83%","44%"],"type":"pie"}],"severity":[],"type":"kpi"},"rect":{"width":200,"height":80}},"data":{"dataName":"{serviceName}_{KPIName}".format(serviceName=nameAndId[2],KPIName=nameAndId[0]),"id":nameAndId[1],"isNotFound":False,"parentId":"{serviceId}".format(serviceId=nameAndId[3]),"type":"kpi"}},"zRotate":0,"anchors":[{"x":546,"y":326.5,"direction":4},{"x":837,"y":268,"direction":1},{"x":1128,"y":326.5,"direction":2},{"x":837,"y":385,"direction":3}],"rotatedAnchors":[{"x":546,"y":326.5,"direction":4},{"x":837,"y":268,"direction":1},{"x":1128,"y":326.5,"direction":2},{"x":837,"y":385,"direction":3}],"animateDuration":0,"animateFrames":[],"borderRadius":0,"iconSize":None,"imageAlign":"center","gradientAngle":0,"gradientRadius":0.01,"paddingTop":0,"paddingBottom":0,"paddingLeft":0,"paddingRight":0,"elementId":"8c5cca5","paddingLeftNum":0,"paddingRightNum":0,"paddingTopNum":0,"paddingBottomNum":0,"textRect":{"x":546,"y":355.75,"width":582,"height":29.25,"center":{"x":837,"y":370.375},"ex":1128,"ey":385},"fullTextRect":{"x":546,"y":268,"width":582,"height":117,"center":{"x":837,"y":326.5},"ex":1128,"ey":385},"iconRect":{"x":546,"y":268,"width":582,"height":87.75,"center":{"x":837,"y":311.875},"ex":1128,"ey":355.75},"fullIconRect":{"x":546,"y":268,"width":582,"height":117,"center":{"x":837,"y":326.5},"ex":1128,"ey":385},"elementRendered":True,"TID":"c576c97","elementLoaded":True,"dockWatchers":[{"x":837,"y":326.5},{"x":306,"y":274},{"x":888,"y":274},{"x":888,"y":391},{"x":306,"y":391}]},
            {"type":0,"rect":{"x":161,"y":286.5,"width":200,"height":80,"center":{"x":261,"y":326.5},"ex":361,"ey":366.5},"lineWidth":1,"rotate":0,"offsetRotate":0,"globalAlpha":1,"dash":0,"strokeStyle":"transparent","fillStyle":"#ffffff","font":{"color":"#000000","fontFamily":"\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial","fontSize":12,"lineHeight":1.5,"fontStyle":"normal","fontWeight":"normal","textAlign":"center","textBaseline":"middle"},"animateCycleIndex":0,"events":[],"eventFns":["link","doAnimate","doFn","doWindowFn"],"id":"f1f3b2c","name":"echarts","tags":[],"lineDashOffset":0,"textOffsetX":0,"textOffsetY":0,"animateType":"","hideInput":True,"visible":True,
            "data":{"text":"{serviceName}_服务健康分数".format(serviceName=nameAndId[2]), "echarts":{"option":{"title":{"text":"服务健康分数","subtext":"","left":"center","top":"bottom","textStyle":{"fontFamily":"Microsoft YaHei","fontSize":12,"fontWeight":"normal","color":"#000000","lineHeight":12,"rich":{"e":{"color":"red"}}},"subtextStyle":{"fontSize":12,"color":"red"}},"tooltip":{"trigger":"axis","padding":[8,12]},"grid":[{"left":2,"right":"32.3%","borderColor":"transparent","top":2,"bottom":24,"backgroundColor":"rgba(0, 0, 0, 0.15)","show":True},{"left":2,"right":"33%","bottom":24,"backgroundColor":"transparent","borderColor":"transparent","show":True},{"x":"68%","right":2,"left":"68%","top":2,"bottom":24,"backgroundColor":"rgba(0, 0, 0, 0.15)","borderColor":"transparent","show":True}],"xAxis":[{"gridIndex":0,"type":"category","data":[],"show":False},{"show":False}],"yAxis":[{"gridIndex":0,"type":"value","show":False},{"show":False}],"series":[{"animation":False,"hoverAnimation":False,"data":[],"smooth":True,"showSymbol":True,"yAxisIndex":0,"symbol":"none","xAxisIndex":0,"symbolSize":0,"type":"line","lineStyle":{"color":"#000000"},"itemStyle":{"color":"#000000"}},{"tooltip":{"trigger":"item","formatter":"N/A","padding":[8,12],"position":["80%","-50%"]},"color":"#000000","animation":False,"avoidLabelOverlap":True,"hoverAnimation":False,"data":[{"value":100,"name":"--"}],"name":"","radius":["46%","46%"],"label":{"show":True,"position":"center","fontSize":20,"formatter":"N/A","rich":{"n":{"fontSize":12}}},"center":["83%","44%"],"type":"pie"}],"severity":[],"type":"service"},"rect":{"width":200,"height":80}},"data":{"dataName":"{serviceName}_服务健康分数".format(serviceName=nameAndId[2]),"id":nameAndId[3],"isNotFound":False,"parentId":"{serviceId}".format(serviceId=nameAndId[3]),"type":"service"}},"zRotate":0,"anchors":[{"x":161,"y":326.5,"direction":4},{"x":261,"y":286.5,"direction":1},{"x":361,"y":326.5,"direction":2},{"x":261,"y":366.5,"direction":3}],"rotatedAnchors":[{"x":161,"y":326.5,"direction":4},{"x":261,"y":286.5,"direction":1},{"x":361,"y":326.5,"direction":2},{"x":261,"y":366.5,"direction":3}],"animateDuration":0,"animateFrames":[],"borderRadius":0,"iconSize":None,"imageAlign":"center","gradientAngle":0,"gradientRadius":0.01,"paddingTop":0,"paddingBottom":0,"paddingLeft":0,"paddingRight":0,"elementId":"aa0e60f","paddingLeftNum":0,"paddingRightNum":0,"paddingTopNum":0,"paddingBottomNum":0,"textRect":{"x":161,"y":346.5,"width":200,"height":20,"center":{"x":261,"y":356.5},"ex":361,"ey":366.5},"fullTextRect":{"x":161,"y":286.5,"width":200,"height":80,"center":{"x":261,"y":326.5},"ex":361,"ey":366.5},"iconRect":{"x":161,"y":286.5,"width":200,"height":60,"center":{"x":261,"y":316.5},"ex":361,"ey":346.5},"fullIconRect":{"x":161,"y":286.5,"width":200,"height":80,"center":{"x":261,"y":326.5},"ex":361,"ey":366.5},"elementRendered":True,"TID":"c576c97","elementLoaded":True,"dockWatchers":[{"x":261,"y":326.5},{"x":-17,"y":292.5},{"x":183,"y":292.5},{"x":183,"y":372.5},{"x":-17,"y":372.5}]},
            {"type":1,"rect":{"x":0,"y":0,"width":0,"height":0,"center":{"x":0,"y":0},"ex":0,"ey":0},"lineWidth":1,"rotate":0,"offsetRotate":0,"globalAlpha":1,"dash":0,"strokeStyle":"#000000","fillStyle":"","font":{"color":"","fontFamily":"\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial","fontSize":12,"lineHeight":1.5,"fontStyle":"normal","fontWeight":"normal","textAlign":"center","textBaseline":"middle","background":"#fff"},"animateCycleIndex":0,"events":[],"eventFns":["link","doAnimate","doFn","doWindowFn"],"id":"335f03","name":"curve","tags":[],"lineDashOffset":0,"textOffsetX":0,"textOffsetY":0,"visible":True,"data":"","controlPoints":[{"x":422,"y":326.5,"direction":2,"anchorIndex":2,"id":"f1f3b2c"},{"x":485,"y":326.5,"direction":4,"anchorIndex":0,"id":"d0c90c4"}],"fromArrowSize":5,"toArrowSize":5,"borderWidth":0,"borderColor":"#000000","animateColor":"","animateSpan":1,"animatePos":0,"isAnimate":False,"animateFromSize":0,"animateToSize":0,"animateDotSize":3,"from":{"x":361,"y":326.5,"direction":2,"anchorIndex":2,"id":"f1f3b2c"},"to":{"x":546,"y":326.5,"direction":4,"anchorIndex":0,"id":"d0c90c4"},"fromArrow":"","toArrow":"straightLine","textRect":None,"TID":"c576c97"},
            {"type":0,"rect":{"x":0,"y":276.5,"width":70,"height":100,"center":{"x":35,"y":326.5},"ex":70,"ey":376.5},"lineWidth":1,"rotate":0,"offsetRotate":0,"globalAlpha":1,"dash":0,"strokeStyle":"#000000","font":{"color":"#000000","fontFamily":"\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial","fontSize":12,"lineHeight":1.5,"fontStyle":"normal","fontWeight":"normal","textAlign":"center","textBaseline":"middle"},"animateCycleIndex":0,"events":[],"eventFns":["link","doAnimate","doFn","doWindowFn"],"id":"ab82928","name":"people","tags":[],"lineDashOffset":0,"textOffsetX":0,"textOffsetY":0,"animateType":"","visible":True,"data":"","zRotate":0,"anchors":[{"x":0,"y":326.5,"direction":4},{"x":35,"y":276.5,"direction":1},{"x":70,"y":326.5,"direction":2},{"x":35,"y":376.5,"direction":3}],"rotatedAnchors":[{"x":0,"y":326.5,"direction":4},{"x":35,"y":276.5,"direction":1},{"x":70,"y":326.5,"direction":2},{"x":35,"y":376.5,"direction":3}],"animateDuration":0,"animateFrames":[],"borderRadius":0,"iconSize":None,"imageAlign":"center","gradientAngle":0,"gradientRadius":0.01,"paddingTop":0,"paddingBottom":0,"paddingLeft":0,"paddingRight":0,"paddingLeftNum":0,"paddingRightNum":0,"paddingTopNum":0,"paddingBottomNum":0,"textRect":{"x":0,"y":0,"width":0,"height":0,"center":{"x":0,"y":0},"ex":0,"ey":0},"fullTextRect":{"x":0,"y":0,"width":0,"height":0,"center":{"x":0,"y":0},"ex":0,"ey":0},"iconRect":{"x":0,"y":0,"width":0,"height":0,"center":{"x":0,"y":0},"ex":0,"ey":0},"elementRendered":False,"TID":"c576c97"},
            {"type":1,"rect":{"x":0,"y":0,"width":0,"height":0,"center":{"x":0,"y":0},"ex":0,"ey":0},"lineWidth":1,"rotate":0,"offsetRotate":0,"globalAlpha":1,"dash":0,"strokeStyle":"#000000","fillStyle":"","font":{"color":"","fontFamily":"\"Hiragino Sans GB\", \"Microsoft YaHei\", \"Helvetica Neue\", Helvetica, Arial","fontSize":12,"lineHeight":1.5,"fontStyle":"normal","fontWeight":"normal","textAlign":"center","textBaseline":"middle","background":"#fff"},"animateCycleIndex":0,"events":[],"eventFns":["link","doAnimate","doFn","doWindowFn"],"id":"19931a69","name":"curve","tags":[],"lineDashOffset":0,"textOffsetX":0,"textOffsetY":0,"visible":True,"data":"","controlPoints":[{"x":100,"y":326.5,"direction":2,"anchorIndex":2,"id":"ab82928"},{"x":131,"y":326.5,"direction":4,"anchorIndex":0,"id":"f1f3b2c"}],"fromArrowSize":5,"toArrowSize":5,"borderWidth":0,"borderColor":"#000000","animateColor":"","animateSpan":1,"animatePos":0,"isAnimate":False,"animateFromSize":0,"animateToSize":0,"animateDotSize":3,"from":{"x":70,"y":326.5,"direction":2,"anchorIndex":2,"id":"ab82928"},"to":{"x":161,"y":326.5,"direction":4,"anchorIndex":0,"id":"f1f3b2c"},"fromArrow":"","toArrow":"straightLine","textRect":None,"TID":"c576c97"}
        ]

        return data


    def getAlertHttpUrl(self):
        if not (self.search):
            return False

        ip = setting.host
        headers = setting.header
        ports = []
        url = 'http://{ip}/etl/input/list?start=0&limit=-1&order=create_time&by=desc'.format(ip=ip)
        rsp = requests.get(url=url,headers=headers)
        inputList=rsp.json()

        for key in self.search:
            for input in inputList:
                if input['id'] == key:
                    ports.append(input['port'])
                    break

        if len(ports) != 1:
            return False

        return 'http://{ip}:{port}'.format(ip=ip,port=ports[0])