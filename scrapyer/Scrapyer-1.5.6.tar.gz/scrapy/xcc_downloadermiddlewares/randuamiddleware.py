"""
browser :选择浏览器头
默认选择:chrome
其他选择:"opera"/"firefox"/"internetexplorer"/"safari"
或者任意ua:"random"
UABROWSER ##选择头
UA_IGNORE_HOSTLIST ##忽略加头host
"""

from oss2.models import ReplicationRule
from .fake_ua import choice_brower_model

class RandomUserAgent(object):
    DEFAULT_BROWSER = 'chrome'
    def __init__(self,uabrowser,ua_ignore_hostlist):
        self.browser = uabrowser #if self.uabrowser else self.DEFAULT_BROWSER
        self.ua_ignore_hostlist = ua_ignore_hostlist
    @classmethod
    def from_crawler(cls, crawler):
        ub=crawler.settings.get('UABROWSER')
        ua_ignore_hostlist = crawler.settings.get("UA_IGNORE_HOSTLIST",[])
        return cls(uabrowser=ub,ua_ignore_hostlist=ua_ignore_hostlist)

    def process_request(self, request, spider):
        def judgement_host(ua_ignore_hostlist,request):
            for ignore_host in ua_ignore_hostlist:
                if ignore_host in  request.url :
                    return True
            return False
        if not judgement_host(self.ua_ignore_hostlist,request) and 'scrapy' in request.headers.get("User-Agent").decode().lower() :
            # 如果在设置hosts中出现将不改变ua
            request.headers["User-Agent"] = choice_brower_model(browser = self.browser)
