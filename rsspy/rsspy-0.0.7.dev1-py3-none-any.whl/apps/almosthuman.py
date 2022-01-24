from rss.base.wechat_public import WechatPublic


class AlmostHuman(WechatPublic):
    def __init__(
            self,
            main_url: str = 'https://www.wxkol.com/show/almosthuman2014.html'):
        super().__init__(main_url, '机器之心')
        self.type += ':almosthuman'
