import ast
import json
import os
import socketserver
import sys

import codefast as cf
from codefast.argparser import PLACEHOLDER

from dofast.flask.config import AUTH_KEY
from dofast.bots.hemabot import Psycho

from .network import (AutoProxy, Bookmark, CoinMarketCap,
                      CustomHTTPRequestHandler, Douban, ForgiveCurve,
                      InputMethod, LunarCalendar, Phone, bitly,
                      shorten_url)
from .oss import Bucket, Message
from .pipe import author
from .security._hmac import generate_token
from .utils import DeeplAPI
from .utils import download as getfile
from .utils import google_translate, shell


def hemabot():
    Psycho.main()


class DCT(dict):
    def __init__(self, data: dict):
        self.data = data

    def format_time(self, seconds: int) -> str:
        if seconds <= 60:
            return f'{seconds}s'
        elif seconds <= 3600:
            return f'{seconds // 60}m ' + self.format_time(seconds % 60)
        else:
            return f'{seconds // 3600}h ' + self.format_time(seconds % 3600)

    def __repr__(self):
        return '\n'.join('{:<10}: {:<10}'.format(p[0], p[1]) for p in (
            ('distance', self.data['distance']),
            ('eta', self.format_time(self.data['eta'])),
            ('station', self.data['stationLeft']))) + '\n'


@cf.utils.retry()
def eta():
    url = 'http://www.bjbus.com/api/api_etartime.php?conditionstr=000000058454081-110100016116032&token=eyJhbGciOiJIUzI1NiIsIlR5cGUiOiJKd3QiLCJ0eXAiOiJKV1QifQ.eyJwYXNzd29yZCI6IjY0ODU5MTQzNSIsInVzZXJOYW1lIjoiYmpidXMiLCJleHAiOjE2MzAxMjA3MDJ9.RIWvu5qeD2iziXk3kOEYJeeRge8hH1OuwDwhGxjew7w'
    headers = {
        'Cookie':
        'SERVERID=564a72c0a566803360ad8bcb09158728|1628475890|1628475881; PHPSESSID=b5f838ce48fc46d99a0f7d9cd7d62aea',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    _config_file = cf.io.home() + '/.config/bus.json'
    if cf.io.exists(_config_file):
        _config = cf.js(_config_file)
        url = _config['url']
        headers['Cookie'] = _config['cookie']

    cf.info(headers)
    res = cf.net.get(url, headers=headers).json()
    cf.info(res)
    data = res['data'][0]['datas']['trip']
    data.sort(key=lambda e: e['distance'])

    for e in data:
        print(DCT(e))


def jsonify() -> dict:
    if len(sys.argv) <= 1:
        print('Usage: jsonify file_name (> export.json)')
        return
    jsf = sys.argv[1]
    assert cf.io.exists(jsf)
    js = cf.js.read(cf.io.read(jsf, ''))
    js = json.dumps(js)
    print(js)


def nsq_sync():
    cli = Bucket()
    if len(sys.argv) > 1:
        cf.utils.shell('zip -r9 -P syncsync63 -FSr /tmp/sync.zip {}'.format(
            ' '.join(sys.argv[1:])))
        cf.info('Files zipped.')
        cli.upload('/tmp/sync.zip')
        token = generate_token(AUTH_KEY, expire=5)
        _uuid = cf.utils.uuid(),
        cf.js.write({'uuid': _uuid}, '/tmp/syncfile.json')
        js = {
            'token': token,
            'topic': 'file',
            'channel': 'sync',
            'uuid': _uuid,
            'data': {
                'uuid': _uuid,
                'filename': 'sync.zip'
            }
        }
        SERVER_HOST = author.get('SERVER_HOST')
        res = cf.net.post(f'http://{SERVER_HOST}:6363/nsq', json=js)
        cf.info('FileSync', res.text)


def _hint_wubi():
    if len(sys.argv) > 1:
        InputMethod().entry(sys.argv[1])


def secure_oss():
    sp = cf.argparser.ArgParser()
    sp.input('-u', '-upload')
    sp.input('-d', '-download')
    sp.parse()

    cli = Bucket()
    cf.utils.shell('mkdir -p /tmp/ossfiles/')

    if sp.upload:
        v = cf.io.basename(sp.upload.value)
        cf.utils.shell(
            f'zip -r0 -P syncsync63 /tmp/ossfiles/{v} {sp.upload.value}')
        cli.upload(f'/tmp/ossfiles/{v}')

    elif sp.download:
        url_prefix = cli.url_prefix
        v = sp.download.value
        getfile(url_prefix + sp.download.value,
                name=f'/tmp/ossfiles/{v}',
                referer=url_prefix.strip('/transfer/'))
        cf.utils.shell(f'unzip -o -P syncsync63 /tmp/ossfiles/{v}')


def main():
    sp = cf.argparser.ArgParser()
    # PLACEHOLDER = cf.argparser.PLACEHOLDER
    sp.input('-cos',
             '--cos',
             sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                       ["l", "list"], ["del", "delete"]])
    sp.input('-oss',
             '--oss',
             sub_args=[["u", "up", "upload"], ["d", "dw", 'download'],
                       ["l", "list"], ["del", "delete"], ['size']])
    sp.input('-dw', '--download', sub_args=[['p', 'proxy']])
    sp.input('-d', '--ddfile')
    sp.input('-ip', '--ip',
             sub_args=[['p', 'port']], default_value="localhost")
    sp.input('-rc', '--roundcorner', sub_args=[['r', 'radius']])
    sp.input('-gu', '--githubupload')
    sp.input('-sm', '--smms')
    sp.input('-yd', '--youdao')
    sp.input('-fd', '--find', sub_args=[['dir', 'directory']])
    sp.input('-m', '--msg', sub_args=[['r', 'read'], ['w', 'write']])
    sp.input('-fund', '--fund', sub_args=[['ba', 'buyalert']])
    sp.input('-stock', '--stock')
    sp.input('-gcr', '--githubcommitreminder')
    sp.input('-pf', '--phoneflow', sub_args=[['rest'], ['daily']])
    sp.input('-hx', '--happyxiao')
    sp.input('-tgbot', '--telegrambot')
    sp.input('-db', '--doubaninfo', description='Get douban film information.')
    sp.input(
        '-sync',
        '--sync',
        description='synchronize files. Usage: sli -sync file1 file2 file3')
    sp.input('-json',
             '--jsonify',
             sub_args=[['o', 'output']],
             description='jsonify single quoted string')
    sp.input('-tt', '-twitter', description='Twitter API.')
    sp.input(
        '-lunar',
        '-lunarcalendar',
        default_value="",
        description='Lunar calendar. Usage:\n sli -lc or sli -lc 2088-09-09.')
    sp.input('-fi', '-fileinfo', description='Get file meta information.')
    sp.input(
        '-st',
        '-securitytext',
        sub_args=[['-d', '-decode'], ['-o', '-output']],
        description='Generate secirty text. Usage: \n sli -st input.txt -o output.txt \n sli -st input.txt -d -o m.txt'
    )

    sp.input(
        '-ap',
        '-autoproxy',
        sub_args=[['-a', '-add'], ['-d', '-delete']],
        description='AutoProxy configuration. Usage:\n sli -ap google.com \n sli -ap -d google.com'
    )

    sp.input(
        '-coin',
        sub_args=[['-q', '-quote']],
        description='Coin Market API. Usage: \n sli -coin -q \n sli -coin -q btc'
    )

    sp.input('-bitly', description='Bitly shorten url.')
    sp.input('-http',
             '-httpserver',
             sub_args=[['p', 'port']],
             description='Simple HTTP server. Usage:\n sli -http -p 8899')

    sp.input('-uni', description='Unicom data flow usage.')
    sp.input(
        '-bm',
        '--bookmark',
        sub_args=[['a', 'add'], ['d', 'delete'], ['l', 'list'], ['o', 'open'],
                  ['reload']],
        description='Make bookmark easier. Usage:\n sli -bm -o google \n sli -bm -a google https://google.com \n sli -bm -d google'
    )

    sp.input('-ebb',
             '-ebbinghaus',
             sub_args=[['r', 'repeat'], ['d', 'delete'], ['a', 'add'],
                       ['reminder']],
             description='\nEbbinghaus forgive curve in usage.')

    sp.input('-e2c', '-excel2csv', description='Extract sheets to CSVs')
    sp.input('-gg', '-google_translate', description='Google translation API.')
    sp.input('-deepl', '-deepl', description='DeepL translation API.')
    sp.input('-pcloud', description='pcloud sync file.')
    sp.input('-botsync', description='sync files from Hema bot')
    sp.input('-ccard',
             sub_args=[['-len', '--length']],
             description='Credit card generator.')
    sp.input('-avatar', description='Generate random avatar.')
    sp.input('-dlj', description='URL shortener.')
    sp.input(
        '-back_translate',
        description='Tranlate text (EN or CH) with Google translator and translate it back with DeepL'
    )
    sp.parse()

    # ------------------------------------
    if sp.back_translate:
        deepl_api = DeeplAPI()
        print(
            deepl_api.translate(
                ast.literal_eval(google_translate(sp.back_translate))['value']))

    elif sp.dlj:
        print(shorten_url(sp.dlj.value))

    elif sp.avatar:
        import dofast.pyavatar as pa
        pa.PyAvataaar().random()

    elif sp.ccard:
        from dofast.toolkits.credit_card_generator import create_cc_numbers
        _len = 16 if not sp.ccard.length else int(sp.ccard.length)
        _bin = '537630' if sp.ccard.value == PLACEHOLDER else sp.ccard.value
        cf.info(_bin, _len)
        for n in create_cc_numbers(_bin, ccnumber_length=_len):
            print(n)

    elif sp.botsync:
        from dofast.toolkits.telegram import download_latest_file
        download_latest_file()

    elif sp.pcloud:
        from dofast.web.pcloud import SyncFile
        SyncFile().sync()

    elif sp.deepl:
        _api = DeeplAPI()
        if sp.deepl.value != PLACEHOLDER:
            _ft = sp.deepl.value
            if cf.io.exists(_ft):
                _api.document(_ft)
            else:
                _api.translate(_ft)
        else:
            _api.stats

    elif sp.google_translate:
        google_translate(sp.google_translate.value)

    elif sp.excel2csv:
        os.system('mkdir -p /tmp/excel/')
        cf.reader.Excel(sp.excel2csv.value).to_csv('/tmp/excel/')

    elif sp.ebbinghaus:
        fc = ForgiveCurve()
        if sp.ebbinghaus.add:
            fc.add_task(sp.ebbinghaus.add)
        elif sp.ebbinghaus.delete:
            fc.remove_task(sp.ebbinghaus.delete)
        elif sp.ebbinghaus.repeat:
            fc.repeat_task(sp.ebbinghaus.repeat)
        elif sp.ebbinghaus.reminder:
            fc.tg_reminder()
        else:
            fc.reminder

    elif sp.bookmark:
        bm = Bookmark()
        if sp.bookmark.open:
            _key, url = sp.bookmark.open, 'http://google.com'
            matched = [(k, v) for k, v in bm.json.items() if _key in k]
            if len(matched) == 1:
                url = matched[0][1]

            elif len(matched) > 1:
                for i, pair in enumerate(matched):
                    print("{:<3} {:<10} {:<10}".format(i, pair[0], pair[1]))
                c = input('Pick one:')
                url = matched[int(c) % len(matched)][1]

            cmd = f'open "{url}"' if 'macos' in cf.os.platform(
            ) else f'xdg-open "{url}"'
            cf.shell(cmd)

        elif sp.bookmark.add:
            _args = sp.bookmark.add
            assert len(_args) == 2, 'Usage: sli -bm -a/-add keyword URL'
            bm.add(keyword=_args[0], url=_args[1])

        elif sp.bookmark.delete:
            _args = sp.bookmark.delete
            if _args.startswith('http'):
                bm.remove(url=_args)
            else:
                bm.remove(keyword=_args)

        elif sp.bookmark.reload:
            bm.reload()

        else:
            bm.list()

    elif sp.uni:
        Phone().unicom()

    elif sp.httpserver:
        port = 8899 if not sp.httpserver.port else int(sp.httpserver.port)
        Handler = CustomHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            cf.logger.info(f"serving at port {port}")
            httpd.serve_forever()

    elif sp.bitly:
        bitly(sp.bitly.value)

    elif sp.coin:
        cmc, _quote = CoinMarketCap(), sp.coin.quote
        if _quote:
            coins = ['BTC', 'ETC', 'ETH', 'SHIB'] if isinstance(
                _quote, dict) else [_quote]
            cmc.part_display(cmc.quote(coins))

    elif sp.autoproxy:
        if sp.autoproxy.delete:
            AutoProxy.delete(sp.autoproxy.delete)
        elif sp.autoproxy.add:
            AutoProxy.add(sp.autoproxy.add)

    elif sp.fileinfo:
        info = cf.io.info(sp.fileinfo.value)
        important_features = {'channel_layout',
                              'channels', 'duration', 'sample_rate'}
        for key in ('bit_rate', 'channel_layout', 'channels',
                    'codec_tag_string', 'codec_long_name', 'codec_name',
                    'duration', 'filename', 'format_name', 'sample_rate',
                    'size', 'width'):
            colortext = cf.fp.green(
                info.get(key, None), attrs=['bold']) if key in important_features else info.get(key, None)
            print('{:<20} {}'.format(key, colortext))

    elif sp.doubaninfo:
        Douban.query_film_info(sp.doubaninfo.value)

    elif sp.twitter:
        @cf.utils.retry()
        def post_status():
            text, media = '', []
            SERVER_HOST = author.get('SERVER_HOST')
            cf.info(SERVER_HOST)
            for e in sys.argv[2:]:
                if cf.io.exists(e):
                    if e.endswith(('.png', '.jpeg', '.jpg', '.mp4', '.gif')):
                        media.append(cf.io.basename(e))
                        cf.net.post(f'http://{SERVER_HOST}:8899',
                                    files={'file': open(e, 'rb')})
                    elif e.endswith(('.txt', '.dat')):
                        text += cf.io.reads(e)
                    else:
                        cf.warning("Unsupported media type", e)
                else:
                    text += e

            def _len(c): return 2 if cf.nstr(c).is_cn() else 1
            all_len = sum(map(_len, text))
            if all_len > 280:
                cf.warning(f'Content too long with length {all_len}')
                return
            text = cf.utils.cipher(AUTH_KEY, text)
            res = cf.net.post(
                f'http://{SERVER_HOST}:6363/tweet',
                json={
                    'text': text,
                    'media': media
                },
                params={'token': generate_token(AUTH_KEY, expire=20)})
            print(res, res.text)
            assert res.text == 'SUCCESS', 'Webo post failed.'

        post_status()

    elif sp.tgbot:
        from .toolkits.telegram import Channel
        Channel('messalert').post(sp.tgbot.value)

    elif sp.happyxiao:
        from .crontasks import HappyXiao
        HappyXiao.rss()

    elif sp.phoneflow:
        from .crontasks import PapaPhone
        if sp.phoneflow.rest:
            PapaPhone.issue_recharge_message()
        elif sp.phoneflow.daily:
            PapaPhone.issue_daily_usage()

    elif sp.githubcommitreminder:
        from .crontasks import GithubTasks
        GithubTasks.git_commit_reminder()
        GithubTasks.tasks_reminder()

    elif sp.cos:
        from .cos import COS
        cli = COS()
        if sp.cos.upload:
            cli.upload_file(sp.cos.upload, "transfer/")
        elif sp.cos.download:
            _file = sp.cos.download
            cli.download_file(f"transfer/{_file}", _file)
        elif sp.cos.delete:
            cli.delete_file(f"transfer/{sp.cos.delete}")
        elif sp.cos.list:
            print(cli.prefix())
            cli.list_files("transfer/")

    elif sp.oss:
        cli = Bucket()
        if sp.oss.upload:
            cli.upload(sp.oss.upload)

        elif sp.oss.download:
            _basename = cf.io.basename(sp.oss.download)
            cli.download(_basename, _basename)

        elif sp.oss.delete:
            cli.delete(sp.oss.delete)
        elif sp.oss.list:
            print(cli.url_prefix)
            if sp.oss.size:
                cli.list_files_by_size()
            else:
                cli.list_files()

    elif sp.sync:
        cli = Bucket()
        files: str = '|'.join(sys.argv[2:])
        if files:
            for f in sys.argv[2:]:
                cli.upload(f.strip())
            cf.json.write({'value': files}, '/tmp/syncsync.json')
            cli.upload('/tmp/syncsync.json')
        else:
            cli.download('syncsync.json')
            files = cf.json.read('syncsync.json')['value'].split('|')
            for f in files:
                getfile(cli.url_prefix + f,
                        referer=cli.url_prefix.strip('/transfer/'))
            os.remove('syncsync.json')

    elif sp.download:
        getfile(sp.download.value, proxy=sp.download.proxy)

    elif sp.ddfile:
        from .utils import create_random_file
        create_random_file(int(sp.ddfile.value or 100))

    elif sp.ip:
        v_ip, v_port = sp.ip.value, sp.ip.port
        from .utils import shell
        if not sp.ip.port:
            print(shell("curl -s cip.cc"))
        else:
            print("Checking on:", v_ip, v_port)
            curl_socks = f"curl -s --connect-timeout 5 --socks5 {v_ip}:{v_port} ipinfo.io"
            curl_http = f"curl -s --connect-timeout 5 --proxy {v_ip}:{v_port} ipinfo.io"
            res = shell(curl_socks)
            if res != '':
                print(res)
            else:
                print('FAILED(socks5 proxy check)')
                print(shell(curl_http))

    elif sp.json:
        jdict = cf.json.eval(sp.json.value)
        print(json.dumps(jdict))
        if sp.json.output:
            cf.json.write(jdict, sp.json.output)

    elif sp.roundcorner:
        from .utils import rounded_corners
        image_path, radius = sys.argv[2], -1
        if len(sys.argv) == 4:
            radius = int(sys.argv[3])
        elif len(sys.argv) == 5:
            radius = int(sys.argv[4])
        rounded_corners(image_path, radius)

    elif sp.githubupload:
        from .utils import githup_upload
        githup_upload(sp.githubupload.value)

    elif sp.smms:
        from .utils import smms_upload
        smms_upload(sp.smms.value)

    elif sp.youdao:
        from .utils import youdao_dict
        youdao_dict(sp.youdao.value)

    elif sp.find:
        from .utils import findfile
        print(sp.find.value, sp.find.directory or '.')
        findfile(sp.find.value, sp.find.directory or '.')

    elif sp.msg:
        if sp.msg.write:
            Message().write(sp.msg.write)
        elif sp.msg.read:
            top_ = 1 if sp.msg.read == {'value': ''} else int(sp.msg.read)
            Message().read(top=top_)     # show only 1 line
        elif sp.msg.value != PLACEHOLDER:
            Message().write(sp.msg.value)
        else:
            Message().read()

    elif sp.fund:
        from .fund import invest_advice, tgalert
        if sp.fund.buyalert:
            tgalert(sp.fund.buyalert)
        else:
            invest_advice(None if sp.fund.value ==
                          PLACEHOLDER else sp.fund.value)

    elif sp.stock:
        from .stock import Stock
        if sp.stock.value != PLACEHOLDER:
            Stock().trend(sp.stock.value)
        else:
            Stock().my_trend()

    elif sp.lunarcalendar:
        date: str = sp.lunarcalendar.value.replace('PLACEHOLDER', '')
        LunarCalendar.display(date)

    else:
        from .data.msg import display_message
        display_message()
        sp.help()
        done, total = sp._arg_counter, 50
        print('✶' * done + '﹆' * (total - done) + "({}/{})".format(done, total))


if __name__ == '__main__':
    main()
