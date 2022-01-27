import typer
import requests
from lxml.etree import HTML
from meutils.notice.wechat import Bot

cli = typer.Typer(name="Tophub")


def get_dom_tree(url="https://top.baidu.com/board?tab=realtime"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE '
    }
    r = requests.get(url, headers=headers)
    return HTML(r.text)


@cli.command()
def send_news(title='今日热榜', url='https://tophub.today/n/x9ozB4KoXb', bot_key='5f51e925-1257-4f90-88ea-f474bc1e2a05'):
    dom_tree = get_dom_tree(url)
    titles = dom_tree.xpath(
        """//*[@id="page"]/div[2]/div[2]/div[1]/div[2]/div/div[1]/table/tbody/tr[*]/td[2]/a/text()"""
    )[:10]
    titles = map(lambda x: x.strip().replace('\n', ' '), titles)
    titles = filter(lambda x: len(x) > 6, titles)
    titles = '\n'.join(map(lambda x: f"{x}", titles)) # {'#' * 8}
    print(titles)

    bot = Bot(bot_key)
    json = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"""
             > # [{title}]({url})\n\n{titles}
             """.strip(),
        }
    }
    bot.send(json)


# if __name__ == '__main__':
#     send_news(title='证券日报', url='https://tophub.today/n/wkvlP5kvz1')
if __name__ == '__main__':
    cli()
