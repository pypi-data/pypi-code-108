from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from .core import ConnectorCore, ConnectorReturn, ConnectorCache, curl_content
from ..utils import parse_date, link_exist_in_db


class AnimeUltime(ConnectorCore):
    color = 'is-warning'
    title = 'Anime-Ultime'
    favicon = 'animeultime.png'
    base_url = 'http://www.anime-ultime.net'
    is_light = True

    def get_full_search_url(self):
        from_date = ''
        sort_type = 'search'

        if self.return_type is ConnectorReturn.HISTORY:
            try:
                page_date = datetime.now() - timedelta((int(self.page) - 1) * 365 / 12)
            except OverflowError:
                page_date = datetime.fromtimestamp(0)
            from_date = page_date.strftime('%m%Y')
            sort_type = 'history'

        return '%s/%s-0-1/%s' % (self.base_url, sort_type, from_date)

    @ConnectorCache.cache_data
    def search(self):
        response = curl_content(self.get_full_search_url(), {
            'search': self.query
        })

        if response['http_code'] == 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            title = html.select('div.title')
            player = html.select('div.AUVideoPlayer')

            if len(title) > 0 and 'Recherche' in title[0].get_text():
                trs = html.select('table.jtable tr')

                for i, tr in enumerate(trs):
                    if not i:
                        continue

                    tds = tr.findAll('td')

                    if len(tds) < 2:
                        continue

                    url = tds[0].a
                    href = '%s/%s' % (self.base_url, url['href'])

                    if not any(href == d['href'] for d in self.data):
                        self.data.append({
                            'vf': self.is_vf(),
                            'href': href,
                            'name': url.get_text(),
                            'type': tds[1].get_text(),
                            'class': self.color if link_exist_in_db(href) else ''
                        })
            elif len(player) > 0:
                name = html.select('h1')
                ani_type = html.select('div.titre')
                href = '%s/file-0-1/%s' % (
                    self.base_url,
                    player[0]['data-serie']
                )

                self.data.append({
                    'vf': self.is_vf(),
                    'href': href,
                    'name': name[0].get_text(),
                    'type': ani_type[0].get_text().replace(':', ''),
                    'class': self.color if link_exist_in_db(href) else ''
                })

            self.on_error = False

    @ConnectorCache.cache_data
    def get_history(self):
        response = curl_content(self.get_full_search_url())

        if response['http_code'] == 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            tables = html.select('table.jtable')
            h3s = html.findAll('h3')

            for i, table in enumerate(tables):
                for j, tr in enumerate(table.findAll('tr')):
                    if not j:
                        continue

                    tds = tr.findAll('td')
                    link = tds[0].a
                    href = '%s/%s' % (self.base_url, link['href'])

                    self.data.append({
                        'vf': self.is_vf(),
                        'href': href,
                        'name': link.get_text(),
                        'type': tds[4].get_text(),
                        'date': parse_date(h3s[i].string[:-3], '%A %d %B %Y'),
                        'class': self.color if link_exist_in_db(href) else ''
                    })

            self.on_error = False

    @ConnectorCache.cache_data
    def is_vf(self, url=''):
        return False
