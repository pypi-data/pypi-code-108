from bs4 import BeautifulSoup

from .core import ConnectorCore, ConnectorReturn, ConnectorCache, curl_content
from ..utils import link_exist_in_db, check_blacklist_words, check_if_vf


class Nyaa(ConnectorCore):
    color = 'is-link'
    title = 'Nyaa'
    favicon = 'nyaa.png'
    base_url = 'https://nyaa.si'
    is_light = False

    def get_full_search_url(self):
        sort_type = 'size'
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 'id'

        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (
            self.query,
            self.query,
            self.query,
            self.query
        )
        return '%s/?f=0&c=1_3&s=%s&o=desc&q=%s&p=%s' % (self.base_url, sort_type, to_query, self.page)

    def get_history(self):
        self.search()

    @ConnectorCache.cache_data
    def search(self):
        response = curl_content(self.get_full_search_url())

        if response['http_code'] == 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            trs = html.select('table.torrent-list tr')
            valid_trs = 0

            for i, tr in enumerate(trs):
                if not i:
                    continue

                tds = tr.findAll('td')
                check_downloads = int(tds[7].get_text())
                check_seeds = int(tds[5].get_text())

                if check_downloads or check_seeds:
                    urls = tds[1].findAll('a')

                    if len(urls) > 1:
                        url = urls[1]
                        has_comment = True
                    else:
                        url = urls[0]
                        has_comment = False

                    url_safe = url.get_text()

                    if check_blacklist_words(url_safe):
                        continue

                    valid_trs = valid_trs + 1
                    href = self.base_url + url['href']

                    self.data.append({
                        'vf': check_if_vf(url_safe),
                        'href': href,
                        'name': url_safe,
                        'comment': str(urls[0]).replace('/view/', self.base_url + '/view/') if has_comment else '',
                        'link': tds[2].decode_contents().replace('/download/', self.base_url + '/download/'),
                        'size': tds[3].get_text(),
                        'date': tds[4].get_text(),
                        'seeds': check_seeds,
                        'leechs': tds[6].get_text(),
                        'downloads': check_downloads,
                        'class': self.color if link_exist_in_db(href) else 'is-%s' % tr['class'][0]
                    })

            self.on_error = False
            self.is_more = valid_trs and valid_trs != len(trs) - 1

    @ConnectorCache.cache_data
    def is_vf(self, url):
        response = curl_content(url)

        if response['http_code'] == 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            title = html.select('h3.panel-title')
            return check_if_vf(title[0].get_text())

        return False
