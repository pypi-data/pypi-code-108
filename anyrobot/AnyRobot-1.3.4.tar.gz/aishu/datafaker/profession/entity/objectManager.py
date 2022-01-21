import urllib.request
from aishu.public.db_select import select

class date(object):
    # Kibana数据库保存对象管理所有的解析规则、仪表盘、搜索、可视化
    # 1.随机获取一个'解析规则'的ruleName
    def getRuleNameId(self):
        sql = 'SELECT ruleName From ParserRule  ORDER BY rand() LIMIT 1'
        rarserRuleName = urllib.parse.quote(select(sql)[0][0])
        return rarserRuleName


    # 2.随机获取一个'仪表盘'的id
    def getDashboardId(self):
        sql = 'SELECT id From Kibana  where Kibana.type = "dashboard" ORDER BY rand() LIMIT 1'
        dashboardId = select(sql)[0][0]
        return dashboardId

    # 3.随机获取一个'搜索'的id
    def getSearchId(self):
        sql = 'SELECT id From Kibana  where Kibana.type = "search" ORDER BY rand() LIMIT 1'
        searchId = select(sql)[0][0]
        return searchId

    # 4.随机获取一个'可视化'的id
    def getVisualizationId(self):
        sql = 'SELECT id From Kibana  where Kibana.type = "visualization" ORDER BY rand() LIMIT 1'
        visualizationId = select(sql)[0][0]
        return visualizationId