''' crontab tasks. '''
import json
import os
import arrow
import re
import socket

import bs4
import codefast as cf
import requests

from .pipe import author
from .toolkits.telegram import Channel
from dofast.vendor.graphviz import Record
socket.setdefaulttimeout(30)

postman = Channel('messalert')


def decode(key: str) -> str:
    return author.get(key)


class PapaPhone:
    url = 'https://h5.ha.chinamobile.com/h5-rest/flow/data'
    params = {'channel': 2, 'version': '6.4.2'}

    @classmethod
    def get_headers(cls):
        h = {}
        h["Cookie"] = decode('cmcc_cookie_2')
        h['Authorization'] = decode('cmcc_authorization_2')
        h["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
        h["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        h['device'] = 'iPhone 7'
        h['Referer'] = 'https://h5.ha.chinamobile.com/hnmccClientWap/h5-rest/'
        return h

    @classmethod
    def query3510(cls) -> dict:
        try:
            resp = requests.get(cls.url,
                                data=cls.params,
                                headers=cls.get_headers()).json()
            res = {'info': '', 'flow': 0}
            for dl in resp['data']['flowList']:
                if not isinstance(dl['details'], list):
                    continue
                for d in dl['details']:
                    res['info'] += f"{d['expireTime']} {d['flowRemain']} {d['name']}\n"
                    flow = re.sub(r'MB|GB', '', d['flowRemain'])
                    flow = float(flow) / 1000 if 'MB' in d[
                        'flowRemain'] else float(flow)
                    res['flow'] += flow
            return res
        except Exception as e:
            cf.error(f'Get data flow from second card failed: {repr(e)}')
            return resp

    @classmethod
    def _query_flow(cls):
        try:
            json_res = requests.get(cls.url,
                                    data=cls.params,
                                    headers=cls.get_headers()).json()
            flow = float(json_res['data']['flowList'][0]['surplusFlow'])
            unit = json_res['data']['flowList'][0]['surplusFlowUnit']
            cf.info(f'Papa iPhone data flow remain {flow} GB.')
            return flow, unit
        except Exception as e:
            cf.error(f'Get data flow failed: {repr(e)}')
            return -1, 'MB'

    @classmethod
    def issue_recharge_message(cls, retry: int = 3) -> None:
        ''' Send alerts via Telegram bot when traffic is lower than 1G '''
        results = cls.query3510()
        cf.info(results)
        if retry <= 0:
            postman.post('手机余量查询失败\n' + '已经连续重试 3 次，全部失败。' + str(results))

        elif 'flow' not in results:
            cls.issue_recharge_message(retry - 1)

        elif results['flow'] < 1:
            message = f"Papa cellphone data flow remain {results['flow']} GB, time to rechage."
            cf.info(message)
            postman.post(message)

    @classmethod
    def draw_flow_image(cls):
        list_ = [('Time', 'Rest', 'Description')]
        texts = cls.query3510().get('info', '')
        for text in texts.split('\n'):
            if not text:
                continue
            date, time, usage, description = text.split(' ')
            list_.append((date + ' ' + time, usage, description))

        return Record('lightyellow').draw_from_list(list_)

    @classmethod
    @cf.utils.retry(total_tries=3)
    def issue_daily_usage(cls):
        image_path = cls.draw_flow_image()
        caption = '[{}] PaPa phone data flow'.format(
            arrow.now().format('YYYY-MM-DD'))
        postman.post_image(image_path, caption)
        cf.info('Phone data flow daily message sent.')


class GithubTasks:
    '''Github related tasks '''
    @classmethod
    def git_commit_reminder(cls) -> None:
        cnt = cls._count_commits()
        prev_cnt, file_ = 10240, 'github.commits.json'
        if os.path.exists(file_):
            prev_cnt = json.load(open(file_, 'r'))['count']
        json.dump({'count': cnt}, open(file_, 'w'), indent=2)

        if cnt > prev_cnt:
            return

        msg = (
            'Github commit reminder \n\n' +
            f"You haven't do any commit today. Your previous commit count is {cnt}"
        )
        postman.post(msg)

    @classmethod
    def tasks_reminder(cls):
        url = decode('GIT_RAW_PREFIX') + '2021/ps.md'

        tasks = cls._request_proxy_get(url).split('\n')
        todo = '\n'.join(t for t in tasks if not t.startswith('- [x]'))
        postman.post('TODO list \n' + todo)

    @classmethod
    def _request_proxy_get(cls, url: str) -> str:
        px = decode('http_proxy').lstrip('http://')
        for _ in range(5):
            try:
                res = requests.get(url,
                                   proxies={'https': px},
                                   headers={'User-Agent': 'Aha'},
                                   timeout=3)
                if res.status_code == 200:
                    return res.text
            except Exception as e:
                print(e)
        else:
            return ''

    @classmethod
    def _count_commits(cls) -> int:
        resp = cls._request_proxy_get(decode('GITHUB_MAINPAGE'))
        if resp:
            soup = bs4.BeautifulSoup(resp, 'lxml')
            h2 = soup.find_all('h2', {'class': 'f4 text-normal mb-2'}).pop()
            commits_count = next(
                int(e) for e in h2.text.split() if e.isdigit())
            return commits_count
        return 0


class HappyXiao:
    ''' happyxiao articles poster'''
    @classmethod
    @cf.utils.retry(total_tries=3)
    def rss(cls, url: str = 'https://happyxiao.com/') -> None:
        rsp = bs4.BeautifulSoup(requests.get(url).text, 'lxml')
        more = rsp.find_all('a', attrs={'class': 'more-link'})
        articles = {m.attrs['href']: '' for m in more}
        jsonfile = 'hx.json'

        if not os.path.exists(jsonfile):
            open(jsonfile, 'w').write('{}')

        j = json.load(open(jsonfile, 'r'))
        res = '\n'.join(cls.brief(k) for k in articles.keys() if k not in j)
        j.update(articles)
        json.dump(j, open(jsonfile, 'w'), indent=2)
        if res:
            postman.post(res.replace('#', '%23'))

    @classmethod
    def brief(cls, url) -> str:
        rsp = bs4.BeautifulSoup(requests.get(url).text, 'lxml')
        art = rsp.find('article')
        res = url + '\n' + art.text.replace('\t', '') + str(art.a)
        return res
