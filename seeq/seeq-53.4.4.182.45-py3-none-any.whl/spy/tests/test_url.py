import pytest

from seeq.spy import _url

from seeq.spy._url import *


@pytest.mark.unit
def test_cleanse_url():
    assert _url.cleanse_url('http://localhost:80') == 'http://localhost'
    assert _url.cleanse_url('http://localhost:443') == 'http://localhost:443'
    assert _url.cleanse_url('https://localhost:80') == 'https://localhost:80'
    assert _url.cleanse_url('https://localhost:443') == 'https://localhost'
    assert _url.cleanse_url('https://chevron.seeq.site/') == 'https://chevron.seeq.site'
    assert _url.cleanse_url('https://chevron.seeq.site:8254/this/is/cool') == 'https://chevron.seeq.site:8254'


@pytest.mark.unit
def test_parse_url():
    urls = [
        ('https://explore.seeq.com'
         '/workbook/4CECFD1D-47C1-4EEC-B664-7BB4A059768F/worksheet/A9364F4E-4B69-44E3-8339-CC1F495859C3',
         SeeqURL(protocol=HttpProtocol.HTTPS,
                 hostname='explore.seeq.com',
                 port=443,
                 route=Route.WORKBOOK_EDIT,
                 workbook_id='4CECFD1D-47C1-4EEC-B664-7BB4A059768F',
                 worksheet_id='A9364F4E-4B69-44E3-8339-CC1F495859C3')),

        ('https://explore.seeq.com'
         '/5802AF02-6764-4E22-8436-1081B69C7A6B/workbook/876C4528-82B3-453B-868E-2334CF5F5CA8'
         '/worksheet/E604E93A-A85E-482E-AEDB-F0944304A7C3',
         SeeqURL(protocol=HttpProtocol.HTTPS,
                 hostname='explore.seeq.com',
                 port=443,
                 route=Route.WORKBOOK_EDIT,
                 folder_id='5802AF02-6764-4E22-8436-1081B69C7A6B',
                 workbook_id='876C4528-82B3-453B-868E-2334CF5F5CA8',
                 worksheet_id='E604E93A-A85E-482E-AEDB-F0944304A7C3')),

        ('http://customer.seeq.site:2445'
         '/view/A2CB408D-4531-438F-B701-FE5AB4974FC1',
         SeeqURL(protocol=HttpProtocol.HTTP,
                 hostname='customer.seeq.site',
                 port=2445,
                 route=Route.WORKBOOK_VIEW,
                 worksheet_id='A2CB408D-4531-438F-B701-FE5AB4974FC1')),

        ('http://customer.seeq.site:2445'
         '/view/A2CB408D-4531-438F-B701-FE5AB4974FC1?workstepId=31344549-F39C-4019-A65E-83082068C86B',
         SeeqURL(protocol=HttpProtocol.HTTP,
                 hostname='customer.seeq.site',
                 port=2445,
                 route=Route.WORKBOOK_VIEW,
                 worksheet_id='A2CB408D-4531-438F-B701-FE5AB4974FC1',
                 workstep_id='31344549-F39C-4019-A65E-83082068C86B')),

        ('https://explore.seeq.com'
         '/present/worksheet/876C4528-82B3-453B-868E-2334CF5F5CA8/E604E93A-A85E-482E-AEDB-F0944304A7C3',
         SeeqURL(protocol=HttpProtocol.HTTPS,
                 hostname='explore.seeq.com',
                 port=443,
                 route=Route.WORKBOOK_PRESENTATION,
                 workbook_id='876C4528-82B3-453B-868E-2334CF5F5CA8',
                 worksheet_id='E604E93A-A85E-482E-AEDB-F0944304A7C3')),

        ('https://explore.seeq.com'
         '/links?type=workstep&workbook=876C4528-82B3-453B-868E-2334CF5F5CA8&'
         'worksheet=E604E93A-A85E-482E-AEDB-F0944304A7C3&amp;workstep=31344549-F39C-4019-A65E-83082068C86B',
         SeeqURL(protocol=HttpProtocol.HTTPS,
                 hostname='explore.seeq.com',
                 port=443,
                 route=Route.JOURNAL_WORKSTEP_LINK,
                 workbook_id='876C4528-82B3-453B-868E-2334CF5F5CA8',
                 worksheet_id='E604E93A-A85E-482E-AEDB-F0944304A7C3',
                 workstep_id='31344549-F39C-4019-A65E-83082068C86B')),

        ('http://customer.seeq.site/workbooks',
         SeeqURL(protocol=HttpProtocol.HTTP,
                 hostname='customer.seeq.site',
                 port=80,
                 route=Route.HOME)),

        ('https://beta.seeq.com/2e4cd73a-0bf9-4e0e-9124-2ba7d3ad8f48/folder/',
         SeeqURL(protocol=HttpProtocol.HTTPS,
                 hostname='beta.seeq.com',
                 port=443,
                 route=Route.HOME,
                 folder_id='2E4CD73A-0BF9-4E0E-9124-2BA7D3AD8F48'))

    ]

    for url, expectation in urls:
        parsed_url = SeeqURL.parse(url)
        assert parsed_url == expectation
        assert parsed_url.url == url.replace('2e4cd73a-0bf9-4e0e-9124-2ba7d3ad8f48',
                                             '2E4CD73A-0BF9-4E0E-9124-2BA7D3AD8F48').replace('&amp;', '&')
