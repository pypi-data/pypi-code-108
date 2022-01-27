import requests
from lxml.etree import HTML
from meutils.notice.wechat import Bot


def get_dom_tree(url="https://top.baidu.com/board?tab=realtime"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE '
    }
    r = requests.get(url, headers=headers)
    return HTML(r.text)


url="https://top.baidu.com/board?tab=realtime"
dom_tree = get_dom_tree(url)
titles = dom_tree.xpath('//*[@id="sanRoot"]/main/div[2]/div/div[2]/div[*]/div[2]/a/div[1]/text()')
scores = dom_tree.xpath('//*[@id="sanRoot"]/main/div[2]/div/div[2]/div[*]/div[1]/div[2]/text()')

titles = '\n'.join(map(str.strip, titles[:10]))

bot = Bot()
json = {
    "msgtype": "markdown",
    "markdown": {
        "content": f"""
         [百度热搜榜Top10]({url})\n{titles}
         """.strip(),
    }
}
bot.send(json)
