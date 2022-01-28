from pynyaata.connectors.core import curl_content
from pynyaata.models import AnimeLink

links = AnimeLink.query.all()

for link in links:
    html = curl_content(link.link, debug=False, cloudflare=True)

    if html['http_code'] != 200 and html['http_code'] != 500:
        print('(%d) %s %s : %s' % (
            html['http_code'],
            link.title.name,
            link.season,
            link.link
        ))
    elif 'darkgray' in str(html['output']):
        print('(darkgray) %s %s : %s' % (
            link.title.name,
            link.season,
            link.link
        ))
