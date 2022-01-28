import re
from datetime import datetime
from urllib.parse import quote

from bs4 import BeautifulSoup

from .core import ConnectorCore, ConnectorReturn, ConnectorCache, curl_content
from ..utils import parse_date, link_exist_in_db, check_blacklist_words, check_if_vf


class YggTorrent(ConnectorCore):
    color = 'is-success'
    title = 'YggTorrent'
    favicon = 'yggtorrent.png'
    base_url = 'https://www3.yggtorrent.re'
    is_light = False
    category = 2179

    def get_full_search_url(self):
        sort_type = 'size'
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 'publish_date'
        sort_page = '&page=%s' % (
            (self.page - 1) * 50
        ) if self.page > 1 else ''

        return '%s/engine/search?name=%s&category=2145&sub_category=%s&do=search&order=desc&sort=%s%s' % (
            self.base_url, self.query, self.category, sort_type, sort_page
        )

    def get_history(self):
        self.search()

    @ConnectorCache.cache_data
    def search(self):
        if self.category:
            response = curl_content(
                self.get_full_search_url(), cloudflare=True
            )

            if response['http_code'] == 200:
                html = BeautifulSoup(response['output'], 'html.parser')
                trs = html.select('table.table tr')
                valid_trs = 0

                for i, tr in enumerate(trs):
                    if not i:
                        continue

                    tds = tr.findAll('td')
                    check_downloads = int(tds[6].get_text())
                    check_seeds = int(tds[7].get_text())

                    if check_downloads or check_seeds:
                        url = tds[1].a
                        url_safe = url.get_text()

                        if check_blacklist_words(url_safe):
                            continue

                        valid_trs = valid_trs + 1

                        self.data.append({
                            'vf': check_if_vf(url_safe),
                            'href': url['href'],
                            'name': url_safe,
                            'comment': '<a href="%s#comm" target="_blank"><i class="fa fa-comments-o"></i>%s</a>' %
                                       (url['href'], tds[3].decode_contents()),
                            'link': '<a href="%s/engine/download_torrent?id=%s">'
                                    '<i class="fa fa-fw fa-download"></i>'
                                    '</a>' % (self.base_url,
                                              re.search(r'/(\d+)', url['href']).group(1)),
                            'size': tds[5].get_text(),
                            'date': parse_date(datetime.fromtimestamp(int(tds[4].div.get_text()))),
                            'seeds': check_seeds,
                            'leechs': tds[8].get_text(),
                            'downloads': check_downloads,
                            'class': self.color if link_exist_in_db(quote(url['href'], '/+:')) else ''
                        })

                self.on_error = False
                self.is_more = valid_trs and valid_trs != len(trs) - 1

    @ConnectorCache.cache_data
    def is_vf(self, url):
        response = curl_content(url)

        if response['http_code'] == 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            title = html.select('#title h1')
            return check_if_vf(title[0].get_text())

        return False


class YggAnimation(YggTorrent):
    title = 'YggAnimation'
    category = 2178
