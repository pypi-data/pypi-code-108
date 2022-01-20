# coding=utf-8
"""
(C) FHCS GmbH

Utilities classes and standalone functions to use for FA API interaction and communication
"""

from datetime import datetime
from html import unescape
from json import dumps
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp


# noinspection DuplicatedCode
def strnorm(strin: str) -> List[str]:
    """
    This does the following:

    -   removes from string all symbols except spaces, latin letters, including UTF-0080+, cyrillic letters
        and digits
    -   uppercases whole string
    -   splits by spaces into the list

    :param strin: given raw string
    :return: list representing the normalized string value
    """
    _ALLOWED = (" 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                "¡¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏ"
                "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя"
                "ѐёђѓєѕіїјљњћќѝўџѠѡѢѣѤѥѦѧѨѩѪѫѬѭѮѯѰѱѲѳѴѵѶѷѸѹѺѻѼѽѾѿҀҁҊҋҌҍҎҏҐґҒғҔҕҖҗҘҙҚқҜҝҞҟҠҡҢңҤҥҦҧҨҩҪҫҬҭ"
                "ҮүҰұҲҳҴҵҶҷҸҹҺһҼҽҾҿӀӁӂӃӄӅӆӇӈӉӊӋӌӍӎӏӐӑӒӓӔӕӖӗӘәӚӛӜӝӞӟӠӡӢӣӤӥӦӧӨөӪӫӬӭӮӯӰӱӲӳӴӵӶӷӸӹӺӻӼӽӾӿ")
    _orig = str(strin)
    _pre = str()
    for _i in _orig:
        if _i in _ALLOWED:
            _pre += _i
        else:
            _pre += chr(0x0020)
    return _pre.upper().split()


def getcookieval(httpsession: aiohttp.ClientSession, cname: str) -> Optional[str]:
    """
    Extract required cookie from aiohttp.CookieJar instance from aiohttp session.

    :param httpsession: Active aiohttp session to use
    :param cname: String name of cookie to extract
    :return: Value of cookie or None if no cookie existing
    """
    for c in httpsession.cookie_jar:
        if c.key == cname:
            return c.value
    return None


def gettag(htmltag: str) -> str:
    """
    Extract content of single HTML tag, normalize with strnorm()

    :param htmltag: String representing one single HTML tag
    :return: Value of tag content, if something wrong with parsing, return the given htmltag value
    """
    _c = htmltag
    _beg = htmltag.find(">")
    if not _beg < 0:
        _end = htmltag.find("<", _beg + 1)
        if not _end < 0:
            _c = htmltag[(_beg + 1):_end]
    if _c != htmltag:
        return chr(0x0020).join(strnorm(unescape(_c)))
    return unescape(htmltag)


async def fagetrefs(fadomain: str,
                    httpsession: aiohttp.ClientSession) -> Tuple[dict, dict, dict, dict, str]:
    """
    Gets users, sites, and spaces from FA API, normalizes all values with strnorm() and runs checks
    to compare API data with those records loaded from MS Excel sheets

    :param fadomain: FA domain name
    :param httpsession: Active aiohttp session to use
    :return: Tuple with four dicts containing normalized values for: user reference, site reference, floors and spaces
             references, and last tuple item is a string with debug log
    """
    # Constant, default SSL certificates check, False to disable certificates check
    _SSL = None
    # Debug log for output
    _debug_log = str()
    # Get all users
    r = await httpsession.post(f"https://{fadomain}.facilityapps.com/api/1.0/users_manager/data",
                               headers={"Accept": "application/json",
                                        "X-CSRF-TOKEN": getcookieval(httpsession, "XSRF-TOKEN")
                                        },
                               params={"fields": FARequests.userquery()},
                               data=FARequests.userform(),
                               ssl=_SSL)
    _users_json = await r.json()
    _debug_log += f"Users received from API:\n{[_u['contact.name'] for _u in _users_json['data']]}" + "\n"
    # Extract our users from whole list
    _user_ref = dict()
    for _i in _users_json["data"]:
        # Normalise the user name with strnorm() and join resulting list with spaces
        _user_ref[chr(0x0020).join(strnorm(unescape(_i["contact.name"])))] = _i["id"]
    _debug_log += f"User reference built:\n{dumps(_user_ref, indent=3, ensure_ascii=False)}" + "\n"
    # Get all sites
    r = await httpsession.post(f"https://{fadomain}.facilityapps.com/api/1.0/site_manager/site_data",
                               headers={"Accept": "application/json",
                                        "X-CSRF-TOKEN": getcookieval(httpsession, "XSRF-TOKEN")
                                        },
                               params={"fields": FARequests.sitequery()},
                               data=FARequests.siteform(),
                               ssl=_SSL)
    _sites_json = await r.json()
    _debug_log += f"Sites received from API:\n{[_s['name'] for _s in _sites_json['data']]}" + "\n"
    # Extract our sites from whole list
    _site_ref = dict()
    for _i in _sites_json["data"]:
        # Normalise the site name with strnorm() and join resulting list with spaces
        _site_ref[chr(0x0020).join(strnorm(unescape(_i["name"])))] = _i["id"]
    _debug_log += f"Sites reference built:\n{dumps(_site_ref, indent=3, ensure_ascii=False)}" + "\n"
    # Get all floors and spaces
    r = await httpsession.post(f"https://{fadomain}.facilityapps.com/api/1.0/floorplan/spaces/list",
                               headers={"Accept": "application/json",
                                        "X-CSRF-TOKEN": getcookieval(httpsession, "XSRF-TOKEN")
                                        },
                               params={"fields": FARequests.spacesquery()},
                               data=FARequests.spacesform(),
                               ssl=_SSL)
    _spaces_json = await r.json()
    # Put IDs of floors and spaces in two reference dicts
    _floors_ref = dict()
    _spaces_ref = dict()
    # Logging counters
    _log_sites = 0
    _log_floors = 0
    _log_spaces = 0
    for _r in _spaces_json["data"]:
        if gettag(_r["site.name"]) not in _spaces_ref.keys():
            _floors_ref[gettag(_r["site.name"])] = dict()
            _spaces_ref[gettag(_r["site.name"])] = dict()
            _log_sites += 1
        if gettag(_r["floor.name"]) not in _spaces_ref[gettag(_r["site.name"])].keys():
            _floors_ref[gettag(_r["site.name"])][gettag(_r["floor.name"])] = unescape(_r["floor.id"])
            _spaces_ref[gettag(_r["site.name"])][gettag(_r["floor.name"])] = dict()
            _log_floors += 1
        if gettag(_r["name"]) not in _spaces_ref[gettag(_r["site.name"])][gettag(_r["floor.name"])].keys():
            _spaces_ref[gettag(_r["site.name"])][gettag(_r["floor.name"])][gettag(_r["name"])] = _r["id"]
            _log_spaces += 1
    _debug_log += f"Got from FA API sites: {_log_sites}, floors: {_log_floors}, spaces: {_log_spaces}" + "\n"
    _debug_log += f"Floors:\n{dumps(_floors_ref, indent=3, ensure_ascii=False)}" + "\n"
    _debug_log += f"Spaces:\n{dumps(_spaces_ref, indent=3, ensure_ascii=False)}" + "\n"
    # Return references
    return _user_ref, _site_ref, _floors_ref, _spaces_ref, _debug_log


# noinspection DuplicatedCode
class FARequests:
    """
    Reference with objects required for FA API requests
    """

    @staticmethod
    def getappversion() -> str:
        """
        :return: FA mobile app version
        """
        return "4.1.0"

    @staticmethod
    def userquery() -> str:
        """
        :return: URL query parameter value to use in request for user list through the API
        """
        return (r'["id","contact\\.name","contact\\.email","contact\\.phonenumber","roles\\.name",'
                r'"lastDevice\\.fapps_version","lastDevice\\.os_version","dummy_lastseen","disablelogin"]')

    @staticmethod
    def sitequery() -> str:
        """
        :return: URL query parameter value to use in request for site list through the API
        """
        return (r'["identifier","name","region\\.name","address\\.city","address\\.address",'
                r'"formSubmissionsToSend\\.id","logboo(kOpenTickets\\.id"]')

    @staticmethod
    def floorsquery() -> str:
        """
        :return: URL query parameter value to use in request for floors list through the API
        """
        return r'["nr","name","site\\.name","level","type","dummy_map"]'

    @staticmethod
    def spacesquery() -> str:
        """
        :return: URL query parameter value to use in request for spaces list through the API
        """
        return r'["nr","name","order","floor\\.name","site\\.name","floor\\.type"]'

    @staticmethod
    def tasksquery() -> str:
        """
        :return: URL query parameter value to use in request for full task list through the API
        """
        return (r'["title","current_status","owners","locations","elements",'
                r'"floor","space","date_start","date_end","date_end"]')

    @staticmethod
    def timeregquery() -> str:
        """
        :return: URL query parameter value to use in request for time reg data through the API
        """
        return (r'["site\\.identifier","site\\.name","type","dummy_name","position\\.name","position\\.code",'
                r'"dummy_hourly_wage","employee\\.personnelnumber","element\\.name","checkin_time",'
                r'"dummy_checkin_location","checkout_time","dummy_checkout_location","total_checkedin_time",'
                r'"dummy_warning","status"]')

    @staticmethod
    def formsreportingquery() -> str:
        """
        :return: URL query parameter value to use in request for forms reporting data through the API
        """
        return (r'["consecutive_nr","form\\.name","site\\.name","element\\.name","employee\\.contact\\.name",'
                r'"user\\.contact\\.name","created_at","url","dummy_images"]')

    @staticmethod
    def userform() -> dict:
        """
        :return: dict with application/x-www-form-urlencoded fields to use in request for user list through the API
        """
        return {"draw": r"5",
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"true",
                "columns[0][orderable]": r"false",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"false",
                "columns[1][data]": r"id",
                "columns[1][name]": r"id",
                "columns[1][searchable]": r"true",
                "columns[1][orderable]": r"true",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"false",
                "columns[2][data]": r"dummy_impersonate",
                "columns[2][name]": r"dummy_impersonate",
                "columns[2][searchable]": r"true",
                "columns[2][orderable]": r"true",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"false",
                "columns[3][data]": r"dummy_logout",
                "columns[3][name]": r"dummy_logout",
                "columns[3][searchable]": r"true",
                "columns[3][orderable]": r"true",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"false",
                "columns[4][data]": r"contact\.name",
                "columns[4][name]": r"contact\.name",
                "columns[4][searchable]": r"true",
                "columns[4][orderable]": r"true",
                "columns[4][search][value]": r"",
                "columns[4][search][regex]": r"false",
                "columns[4][contact_name]": r"true",
                "columns[5][data]": r"contact\.email",
                "columns[5][name]": r"contact\.email",
                "columns[5][searchable]": r"true",
                "columns[5][orderable]": r"true",
                "columns[5][search][value]": r"",
                "columns[5][search][regex]": r"false",
                "columns[6][data]": r"contact\.phonenumber",
                "columns[6][name]": r"contact\.phonenumber",
                "columns[6][searchable]": r"true",
                "columns[6][orderable]": r"true",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"false",
                "columns[7][data]": r"roles\.name",
                "columns[7][name]": r"roles\.name",
                "columns[7][searchable]": r"true",
                "columns[7][orderable]": r"true",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"false",
                "columns[7][concat][separator]": r"', '",
                "columns[8][data]": r"lastDevice\.fapps_version",
                "columns[8][name]": r"lastDevice\.fapps_version",
                "columns[8][searchable]": r"true",
                "columns[8][orderable]": r"true",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"false",
                "columns[9][data]": r"lastDevice\.device_type",
                "columns[9][name]": r"lastDevice\.device_type",
                "columns[9][searchable]": r"true",
                "columns[9][orderable]": r"true",
                "columns[9][search][value]": r"",
                "columns[9][search][regex]": r"false",
                "columns[10][data]": r"lastDevice\.os_version",
                "columns[10][name]": r"lastDevice\.os_version",
                "columns[10][searchable]": r"true",
                "columns[10][orderable]": r"true",
                "columns[10][search][value]": r"",
                "columns[10][search][regex]": r"false",
                "columns[11][data]": r"dummy_lastseen",
                "columns[11][name]": r"dummy_lastseen",
                "columns[11][searchable]": r"true",
                "columns[11][orderable]": r"true",
                "columns[11][search][value]": r"",
                "columns[11][search][regex]": r"false",
                "columns[12][data]": r"disablelogin",
                "columns[12][name]": r"disablelogin",
                "columns[12][searchable]": r"true",
                "columns[12][orderable]": r"true",
                "columns[12][search][value]": r"",
                "columns[12][search][regex]": r"false",
                "columns[13][data]": r"displayColumns",
                "columns[13][name]": r"",
                "columns[13][searchable]": r"true",
                "columns[13][orderable]": r"false",
                "columns[13][search][value]": r"",
                "columns[13][search][regex]": r"false",
                "order[0][column]": r"1",
                "order[0][dir]": r"asc",
                "start": r"0",
                "length": str(2 ** 16),
                "search[value]": r"",
                "search[regex]": r"false"
                }

    @staticmethod
    def siteform() -> dict:
        """
        :return: dict with application/x-www-form-urlencoded fields to use in request for site list through the API
        """
        return {"draw": r"1",
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"true",
                "columns[0][orderable]": r"false",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"false",
                "columns[1][data]": r"id",
                "columns[1][name]": r"id",
                "columns[1][searchable]": r"true",
                "columns[1][orderable]": r"true",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"false",
                "columns[2][data]": r"identifier",
                "columns[2][name]": r"identifier",
                "columns[2][searchable]": r"true",
                "columns[2][orderable]": r"true",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"false",
                "columns[3][data]": r"name",
                "columns[3][name]": r"name",
                "columns[3][searchable]": r"true",
                "columns[3][orderable]": r"true",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"false",
                "columns[4][data]": r"region\.name",
                "columns[4][name]": r"region\.name",
                "columns[4][searchable]": r"true",
                "columns[4][orderable]": r"true",
                "columns[4][search][value]": r"",
                "columns[4][search][regex]": r"false",
                "columns[5][data]": r"address\.city",
                "columns[5][name]": r"address\.city",
                "columns[5][searchable]": r"true",
                "columns[5][orderable]": r"true",
                "columns[5][search][value]": r"",
                "columns[5][search][regex]": r"false",
                "columns[6][data]": r"address\.address",
                "columns[6][name]": r"address\.address",
                "columns[6][searchable]": r"true",
                "columns[6][orderable]": r"true",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"false",
                "columns[7][data]": r"formSubmissionsToSend\.id",
                "columns[7][name]": r"formSubmissionsToSend\.id",
                "columns[7][searchable]": r"true",
                "columns[7][orderable]": r"true",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"false",
                "columns[7][allowed_join]": r"true",
                "columns[8][data]": r"logbookOpenTickets\.id",
                "columns[8][name]": r"logbookOpenTickets\.id",
                "columns[8][searchable]": r"true",
                "columns[8][orderable]": r"true",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"false",
                "columns[9][data]": r"displayColumns",
                "columns[9][name]": r"",
                "columns[9][searchable]": r"true",
                "columns[9][orderable]": r"false",
                "columns[9][search][value]": r"",
                "columns[9][search][regex]": r"false",
                "order[0][column]": r"1",
                "order[0][dir]": r"asc",
                "start": r"0",
                "length": str(2 ** 16),
                "search[value]": r"",
                "search[regex]": r"false"
                }

    @staticmethod
    def floorsform(draw: Optional[int] = None,
                   sitename: Optional[str] = None,
                   start: Optional[int] = None,
                   count: Optional[int] = None) -> dict:
        """
        :param draw: draw ID, sequental
        :param sitename: if given, then search for items only under this site name
        :param start: if given, then the indexed starting task to return from
        :param count: if given, then it is the count of tasks to return
        :return: dict with application/x-www-form-urlencoded fields to use in request for
                 floors through the API
        """
        if isinstance(draw, int):
            _draw = draw
        else:
            _draw = 1
        if isinstance(sitename, str):
            _sitename = sitename
        else:
            _sitename = str()
        if isinstance(start, int) and isinstance(count, int):
            _start = start
            _count = count
        else:
            _start = 0
            _count = 2 ** 31 - 1
        return {"draw": str(_draw),
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"TRUE",
                "columns[0][orderable]": r"FALSE",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"FALSE",
                "columns[1][data]": r"nr",
                "columns[1][name]": r"nr",
                "columns[1][searchable]": r"TRUE",
                "columns[1][orderable]": r"TRUE",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"FALSE",
                "columns[2][data]": r"name",
                "columns[2][name]": r"name",
                "columns[2][searchable]": r"TRUE",
                "columns[2][orderable]": r"TRUE",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"FALSE",
                "columns[3][data]": r"site\.id",
                "columns[3][name]": r"site\.id",
                "columns[3][searchable]": r"TRUE",
                "columns[3][orderable]": r"TRUE",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"FALSE",
                "columns[4][data]": r"site\.name",
                "columns[4][name]": r"site\.name",
                "columns[4][searchable]": r"TRUE",
                "columns[4][orderable]": r"TRUE",
                "columns[4][search][value]": _sitename,
                "columns[4][search][regex]": r"FALSE",
                "columns[5][data]": r"level",
                "columns[5][name]": r"level",
                "columns[5][searchable]": r"TRUE",
                "columns[5][orderable]": r"TRUE",
                "columns[5][search][value]": r"",
                "columns[5][search][regex]": r"FALSE",
                "columns[6][data]": r"type",
                "columns[6][name]": r"type",
                "columns[6][searchable]": r"TRUE",
                "columns[6][orderable]": r"TRUE",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"FALSE",
                "columns[7][data]": r"dummy_map",
                "columns[7][name]": r"dummy_map",
                "columns[7][searchable]": r"TRUE",
                "columns[7][orderable]": r"TRUE",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"FALSE",
                "columns[8][data]": r"displayColumns",
                "columns[8][name]": r"",
                "columns[8][searchable]": r"TRUE",
                "columns[8][orderable]": r"FALSE",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"FALSE",
                "order[0][column]": r"1",
                "order[0][dir]": r"asc",
                "start": str(_start),
                "length": str(_count),
                "search[value]": r"",
                "search[regex]": r"FALSE"
                }

    @staticmethod
    def spacesform(draw: Optional[int] = None,
                   sitename: Optional[str] = None,
                   start: Optional[int] = None,
                   count: Optional[int] = None) -> dict:
        """
        :param draw: draw ID, sequental
        :param sitename: if given, then search for items only under this site name
        :param start: if given, then the indexed starting task to return from
        :param count: if given, then it is the count of tasks to return
        :return: dict with application/x-www-form-urlencoded fields to use in request for
                 spaces through the API
        """
        if isinstance(draw, int):
            _draw = draw
        else:
            _draw = 1
        if isinstance(sitename, str):
            _sitename = sitename
        else:
            _sitename = str()
        if isinstance(start, int) and isinstance(count, int):
            _start = start
            _count = count
        else:
            _start = 0
            _count = 2 ** 31 - 1
        return {"draw": str(_draw),
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"true",
                "columns[0][orderable]": r"false",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"false",
                "columns[1][data]": r"nr",
                "columns[1][name]": r"nr",
                "columns[1][searchable]": r"true",
                "columns[1][orderable]": r"true",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"false",
                "columns[2][data]": r"name",
                "columns[2][name]": r"name",
                "columns[2][searchable]": r"true",
                "columns[2][orderable]": r"true",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"false",
                "columns[3][data]": r"order",
                "columns[3][name]": r"order",
                "columns[3][searchable]": r"true",
                "columns[3][orderable]": r"true",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"false",
                "columns[4][data]": r"floor\.id",
                "columns[4][name]": r"floor\.id",
                "columns[4][searchable]": r"true",
                "columns[4][orderable]": r"true",
                "columns[4][search][value]": _sitename,
                "columns[4][search][regex]": r"false",
                "columns[5][data]": r"floor\.name",
                "columns[5][name]": r"floor\.name",
                "columns[5][searchable]": r"true",
                "columns[5][orderable]": r"true",
                "columns[5][search][value]": r"",
                "columns[5][search][regex]": r"false",
                "columns[6][data]": r"site\.id",
                "columns[6][name]": r"site\.id",
                "columns[6][searchable]": r"true",
                "columns[6][orderable]": r"true",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"false",
                "columns[7][data]": r"site\.name",
                "columns[7][name]": r"site\.name",
                "columns[7][searchable]": r"true",
                "columns[7][orderable]": r"true",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"false",
                "columns[8][data]": r"floor\.type",
                "columns[8][name]": r"floor\.type",
                "columns[8][searchable]": r"true",
                "columns[8][orderable]": r"true",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"false",
                "order[0][column]": r"1",
                "order[0][dir]": r"asc",
                "start": str(_start),
                "length": str(_count),
                "search[value]": r"",
                "search[regex]": r"false"
                }

    @staticmethod
    def tasksform(draw: int,
                  tbeg: datetime,
                  tend: datetime,
                  start: Optional[int] = None,
                  count: Optional[int] = None) -> dict:
        """
        Returns form fields to request full tasks list, for period from tbeg till tend,
        and pagination is also possible using start and count parameters, default is to return all available tasks.

        :param draw: draw ID, sequental
        :param tbeg: date and time from which to select tasks
        :param tend: date and time till which to select tasks
        :param start: if given, then the indexed starting task to return from
        :param count: if given, then it is the count of tasks to return
        :return: dict with application/x-www-form-urlencoded fields
        """
        if isinstance(start, int) and isinstance(count, int):
            _start = start
            _count = count
        else:
            _start = 0
            _count = 2 ** 31 - 1
        return {"draw": str(draw),
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"true",
                "columns[0][orderable]": r"false",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"false",
                "columns[1][data]": r"id",
                "columns[1][name]": r"id",
                "columns[1][searchable]": r"true",
                "columns[1][orderable]": r"true",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"false",
                "columns[2][data]": r"title",
                "columns[2][name]": r"title",
                "columns[2][searchable]": r"true",
                "columns[2][orderable]": r"true",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"false",
                "columns[3][data]": r"current_status",
                "columns[3][name]": r"current_status",
                "columns[3][searchable]": r"true",
                "columns[3][orderable]": r"true",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"false",
                "columns[4][data]": r"owners",
                "columns[4][name]": r"owners",
                "columns[4][searchable]": r"true",
                "columns[4][orderable]": r"true",
                "columns[4][search][value]": r"",
                "columns[4][search][regex]": r"false",
                "columns[5][data]": r"locations",
                "columns[5][name]": r"locations",
                "columns[5][searchable]": r"true",
                "columns[5][orderable]": r"true",
                "columns[5][search][value]": r"All",
                "columns[5][search][regex]": r"false",
                "columns[6][data]": r"elements",
                "columns[6][name]": r"elements",
                "columns[6][searchable]": r"true",
                "columns[6][orderable]": r"true",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"false",
                "columns[7][data]": r"floor",
                "columns[7][name]": r"floor",
                "columns[7][searchable]": r"true",
                "columns[7][orderable]": r"true",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"false",
                "columns[8][data]": r"space",
                "columns[8][name]": r"space",
                "columns[8][searchable]": r"true",
                "columns[8][orderable]": r"true",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"false",
                "columns[9][data]": r"hour_start",
                "columns[9][name]": r"hour_start",
                "columns[9][searchable]": r"true",
                "columns[9][orderable]": r"true",
                "columns[9][search][value]": r"",
                "columns[9][search][regex]": r"false",
                "columns[10][data]": r"minute_start",
                "columns[10][name]": r"minute_start",
                "columns[10][searchable]": r"true",
                "columns[10][orderable]": r"true",
                "columns[10][search][value]": r"",
                "columns[10][search][regex]": r"false",
                "columns[11][data]": r"hour_end",
                "columns[11][name]": r"hour_end",
                "columns[11][searchable]": r"true",
                "columns[11][orderable]": r"true",
                "columns[11][search][value]": r"",
                "columns[11][search][regex]": r"false",
                "columns[12][data]": r"minute_end",
                "columns[12][name]": r"minute_end",
                "columns[12][searchable]": r"true",
                "columns[12][orderable]": r"true",
                "columns[12][search][value]": r"",
                "columns[12][search][regex]": r"false",
                "columns[13][data]": r"date_start",
                "columns[13][name]": r"date_start",
                "columns[13][searchable]": r"true",
                "columns[13][orderable]": r"true",
                "columns[13][search][value]": r"",
                "columns[13][search][regex]": r"false",
                "columns[14][data]": r"date_end",
                "columns[14][name]": r"date_end",
                "columns[14][searchable]": r"true",
                "columns[14][orderable]": r"true",
                "columns[14][search][value]": r"",
                "columns[14][search][regex]": r"false",
                "columns[15][data]": r"date_end",
                "columns[15][name]": r"date_end",
                "columns[15][searchable]": r"true",
                "columns[15][orderable]": r"true",
                "columns[15][search][value]": r"",
                "columns[15][search][regex]": r"false",
                "order[0][column]": r"13",
                "order[0][dir]": r"asc",
                "start": str(_start),
                "length": str(_count),
                "search[value]": r"",
                "search[regex]": r"false",
                "dates[from]": tbeg.strftime("%Y-%m-%d"),
                "dates[to]": tend.strftime("%Y-%m-%d"),
                "dateColumn": r"date_end",
                "timeColumn": r"false"
                }

    @staticmethod
    def apploginform(usr: str, pwd: str) -> Dict[str, Any]:
        """
        :param usr: username string to use for login
        :param pwd: password string to use for login
        :return: dict with application/x-www-form-urlencoded fields to use for app API login request
        """
        return {"T": "LogIn_v2",
                "username": usr,
                "password": pwd,
                "session_id": str(),
                "version": FARequests.getappversion(),
                "mode": "LogIn",
                "auth_method": "basic"
                }

    @staticmethod
    def applogbookform(formdata: Union[Dict, List], siteid: int, sid: str) -> Dict[str, Any]:
        """
        :param formdata: JSON serializable object representing the form data
        :param siteid: integer site ID for FA API
        :param sid: session_id token got from login
        :return: dict with application/x-www-form-urlencoded fields to use for app API new logbook item submit
        """
        return {"T": "FormCheckList_v11",
                "L": "ru_RU",
                "FormData": dumps(formdata, ensure_ascii=False),
                "ReferenceId": str(siteid),
                "ReferenceType": "1",
                "Timestamp": str(int(time())),
                "session_id": sid,
                "AppVersionNumber": FARequests.getappversion(),
                "TaskData": "null"
                }

    @staticmethod
    def appchecklistsform(sid: str) -> Dict[str, Any]:
        """
        :param sid: session_id token got from login
        :return: dict with application/x-www-form-urlencoded fields to use for app API GetChecklists request
        """
        return {"session_id": sid,
                "T": "GetChecklists",
                "L": "ru_RU",
                "region_code": "ru_RU"
                }

    @staticmethod
    def appchecklistquestionsform(formids: List[int], sid: str) -> Dict[str, Any]:
        """
        :param formids: list of integer checklists IDs for FA API
        :param sid: session_id token got from login
        :return: dict with application/x-www-form-urlencoded fields to use for app API getChecklistQuestions request
        """
        return {"session_id": sid,
                "T": "getChecklistQuestions_v6",
                "checkListID": ";".join([str(_i) for _i in formids]),
                "image_data": "false",
                "region_code": "ru_RU"
                }

    @staticmethod
    def timeregform(draw: int,
                    tbeg: datetime,
                    tend: datetime,
                    start: Optional[int] = None,
                    count: Optional[int] = None) -> dict:
        """
        Returns form fields to request time registration data, for period from tbeg till tend,
        and pagination is also possible using start and count parameters, default is to return all available entries.

        :param draw: draw ID, sequental
        :param tbeg: date and time from which to select tasks
        :param tend: date and time till which to select tasks
        :param start: if given, then the indexed starting task to return from
        :param count: if given, then it is the count of tasks to return
        :return: dict with application/x-www-form-urlencoded fields
        """
        if isinstance(start, int) and isinstance(count, int):
            _start = start
            _count = count
        else:
            _start = 0
            _count = 2 ** 31 - 1
        return {"draw": str(draw),
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"true",
                "columns[0][orderable]": r"false",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"false",
                "columns[1][data]": r"id",
                "columns[1][name]": r"id",
                "columns[1][searchable]": r"true",
                "columns[1][orderable]": r"true",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"false",
                "columns[2][data]": r"site\.identifier",
                "columns[2][name]": r"site\.identifier",
                "columns[2][searchable]": r"true",
                "columns[2][orderable]": r"true",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"false",
                "columns[3][data]": r"site\.deleted_at",
                "columns[3][name]": r"site\.deleted_at",
                "columns[3][searchable]": r"true",
                "columns[3][orderable]": r"true",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"false",
                "columns[3][timestamp]": r"true",
                "columns[4][data]": r"site\.name",
                "columns[4][name]": r"site\.name",
                "columns[4][searchable]": r"true",
                "columns[4][orderable]": r"true",
                "columns[4][search][value]": r"",
                "columns[4][search][regex]": r"false",
                "columns[4][absolute_search]": r"true",
                "columns[5][data]": r"clockDataCheckOut\.floor\.name",
                "columns[5][name]": r"clockDataCheckOut\.floor\.name",
                "columns[5][searchable]": r"true",
                "columns[5][orderable]": r"true",
                "columns[5][search][value]": r"",
                "columns[5][search][regex]": r"false",
                "columns[6][data]": r"clockDataCheckOut\.space\.name",
                "columns[6][name]": r"clockDataCheckOut\.space\.name",
                "columns[6][searchable]": r"true",
                "columns[6][orderable]": r"true",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"false",
                "columns[7][data]": r"clockDataCheckIn\.floor\.name",
                "columns[7][name]": r"clockDataCheckIn\.floor\.name",
                "columns[7][searchable]": r"true",
                "columns[7][orderable]": r"true",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"false",
                "columns[8][data]": r"clockDataCheckIn\.space\.name",
                "columns[8][name]": r"clockDataCheckIn\.space\.name",
                "columns[8][searchable]": r"true",
                "columns[8][orderable]": r"true",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"false",
                "columns[9][data]": r"type",
                "columns[9][name]": r"type",
                "columns[9][searchable]": r"true",
                "columns[9][orderable]": r"true",
                "columns[9][search][value]": r"",
                "columns[9][search][regex]": r"false",
                "columns[9][absolute_search]": r"true",
                "columns[10][data]": r"user\.deleted_at",
                "columns[10][name]": r"user\.deleted_at",
                "columns[10][searchable]": r"true",
                "columns[10][orderable]": r"true",
                "columns[10][search][value]": r"",
                "columns[10][search][regex]": r"false",
                "columns[10][timestamp]": r"true",
                "columns[11][data]": r"employee\.deleted_at",
                "columns[11][name]": r"employee\.deleted_at",
                "columns[11][searchable]": r"true",
                "columns[11][orderable]": r"true",
                "columns[11][search][value]": r"",
                "columns[11][search][regex]": r"false",
                "columns[11][timestamp]": r"true",
                "columns[12][data]": r"dummy_name",
                "columns[12][name]": r"dummy_name",
                "columns[12][searchable]": r"true",
                "columns[12][orderable]": r"true",
                "columns[12][search][value]": r"",
                "columns[12][search][regex]": r"false",
                "columns[13][data]": r"user\.contact\.name",
                "columns[13][name]": r"user\.contact\.name",
                "columns[13][searchable]": r"true",
                "columns[13][orderable]": r"true",
                "columns[13][search][value]": r"",
                "columns[13][search][regex]": r"false",
                "columns[13][absolute_search]": r"true",
                "columns[13][contact_name]": r"true",
                "columns[13][default_display]": r"false",
                "columns[14][data]": r"employee\.contact\.name",
                "columns[14][name]": r"employee\.contact\.name",
                "columns[14][searchable]": r"true",
                "columns[14][orderable]": r"true",
                "columns[14][search][value]": r"",
                "columns[14][search][regex]": r"false",
                "columns[14][absolute_search]": r"true",
                "columns[14][contact_name]": r"true",
                "columns[14][default_display]": r"false",
                "columns[15][data]": r"position\.deleted_at",
                "columns[15][name]": r"position\.deleted_at",
                "columns[15][searchable]": r"true",
                "columns[15][orderable]": r"true",
                "columns[15][search][value]": r"",
                "columns[15][search][regex]": r"false",
                "columns[15][timestamp]": r"true",
                "columns[16][data]": r"position\.name",
                "columns[16][name]": r"position\.name",
                "columns[16][searchable]": r"true",
                "columns[16][orderable]": r"true",
                "columns[16][search][value]": r"",
                "columns[16][search][regex]": r"false",
                "columns[16][translated]": r"true",
                "columns[17][data]": r"position\.code",
                "columns[17][name]": r"position\.code",
                "columns[17][searchable]": r"true",
                "columns[17][orderable]": r"true",
                "columns[17][search][value]": r"",
                "columns[17][search][regex]": r"false",
                "columns[18][data]": r"dummy_hourly_wage",
                "columns[18][name]": r"dummy_hourly_wage",
                "columns[18][searchable]": r"true",
                "columns[18][orderable]": r"false",
                "columns[18][search][value]": r"",
                "columns[18][search][regex]": r"false",
                "columns[19][data]": r"employee\.personnelnumber",
                "columns[19][name]": r"employee\.personnelnumber",
                "columns[19][searchable]": r"true",
                "columns[19][orderable]": r"true",
                "columns[19][search][value]": r"",
                "columns[19][search][regex]": r"false",
                "columns[20][data]": r"element\.deleted_at",
                "columns[20][name]": r"element\.deleted_at",
                "columns[20][searchable]": r"true",
                "columns[20][orderable]": r"true",
                "columns[20][search][value]": r"",
                "columns[20][search][regex]": r"false",
                "columns[20][timestamp]": r"true",
                "columns[21][data]": r"element\.name",
                "columns[21][name]": r"element\.name",
                "columns[21][searchable]": r"true",
                "columns[21][orderable]": r"true",
                "columns[21][search][value]": r"",
                "columns[21][search][regex]": r"false",
                "columns[21][translated]": r"true",
                "columns[22][data]": r"checkin_time",
                "columns[22][name]": r"checkin_time",
                "columns[22][searchable]": r"true",
                "columns[22][orderable]": r"true",
                "columns[22][search][value]": r"",
                "columns[22][search][regex]": r"false",
                "columns[23][data]": r"dummy_checkin_date",
                "columns[23][name]": r"dummy_checkin_date",
                "columns[23][searchable]": r"true",
                "columns[23][orderable]": r"true",
                "columns[23][search][value]": r"",
                "columns[23][search][regex]": r"false",
                "columns[23][default_display]": r"false",
                "columns[24][data]": r"dummy_checkin_time",
                "columns[24][name]": r"dummy_checkin_time",
                "columns[24][searchable]": r"true",
                "columns[24][orderable]": r"true",
                "columns[24][search][value]": r"",
                "columns[24][search][regex]": r"false",
                "columns[24][default_display]": r"false",
                "columns[25][data]": r"dummy_checkin_location",
                "columns[25][name]": r"dummy_checkin_location",
                "columns[25][searchable]": r"true",
                "columns[25][orderable]": r"false",
                "columns[25][search][value]": r"",
                "columns[25][search][regex]": r"false",
                "columns[26][data]": r"checkout_time",
                "columns[26][name]": r"checkout_time",
                "columns[26][searchable]": r"true",
                "columns[26][orderable]": r"true",
                "columns[26][search][value]": r"",
                "columns[26][search][regex]": r"false",
                "columns[27][data]": r"dummy_checkout_date",
                "columns[27][name]": r"dummy_checkout_date",
                "columns[27][searchable]": r"true",
                "columns[27][orderable]": r"true",
                "columns[27][search][value]": r"",
                "columns[27][search][regex]": r"false",
                "columns[27][default_display]": r"false",
                "columns[28][data]": r"dummy_checkout_time",
                "columns[28][name]": r"dummy_checkout_time",
                "columns[28][searchable]": r"true",
                "columns[28][orderable]": r"true",
                "columns[28][search][value]": r"",
                "columns[28][search][regex]": r"false",
                "columns[28][default_display]": r"false",
                "columns[29][data]": r"dummy_checkout_location",
                "columns[29][name]": r"dummy_checkout_location",
                "columns[29][searchable]": r"true",
                "columns[29][orderable]": r"false",
                "columns[29][search][value]": r"",
                "columns[29][search][regex]": r"false",
                "columns[30][data]": r"total_checkedin_time",
                "columns[30][name]": r"total_checkedin_time",
                "columns[30][searchable]": r"true",
                "columns[30][orderable]": r"true",
                "columns[30][search][value]": r"",
                "columns[30][search][regex]": r"false",
                "columns[31][data]": r"dummy_task",
                "columns[31][name]": r"dummy_task",
                "columns[31][searchable]": r"true",
                "columns[31][orderable]": r"true",
                "columns[31][search][value]": r"",
                "columns[31][search][regex]": r"false",
                "columns[32][data]": r"taskClockLog\.task_id",
                "columns[32][name]": r"taskClockLog\.task_id",
                "columns[32][searchable]": r"true",
                "columns[32][orderable]": r"true",
                "columns[32][search][value]": r"",
                "columns[32][search][regex]": r"false",
                "columns[33][data]": r"taskClockLog\.sequence_number",
                "columns[33][name]": r"taskClockLog\.sequence_number",
                "columns[33][searchable]": r"true",
                "columns[33][orderable]": r"true",
                "columns[33][search][value]": r"",
                "columns[33][search][regex]": r"false",
                "columns[34][data]": r"dummy_warning",
                "columns[34][name]": r"dummy_warning",
                "columns[34][searchable]": r"true",
                "columns[34][orderable]": r"false",
                "columns[34][search][value]": r"",
                "columns[34][search][regex]": r"false",
                "columns[35][data]": r"status",
                "columns[35][name]": r"status",
                "columns[35][searchable]": r"true",
                "columns[35][orderable]": r"true",
                "columns[35][search][value]": r"",
                "columns[35][search][regex]": r"false",
                "columns[36][data]": r"displayColumns",
                "columns[36][name]": r"",
                "columns[36][searchable]": r"true",
                "columns[36][orderable]": r"false",
                "columns[36][search][value]": r"",
                "columns[36][search][regex]": r"false",
                "order[0][column]": r"6",
                "order[0][dir]": r"desc",
                "start": str(_start),
                "length": str(_count),
                "search[value]": r"",
                "search[regex]": r"false",
                "dates[from]": str(int(tbeg.timestamp())),
                "dates[to]": str(int(tend.timestamp())),
                "dateColumn": r"checkin_time",
                "timeColumn": r"false"
                }

    @staticmethod
    def formsreportingform(draw: int,
                           tbeg: datetime,
                           tend: datetime,
                           start: Optional[int] = None,
                           count: Optional[int] = None) -> dict:
        """
        Returns form fields to request submitted forms list, for period from tbeg till tend,
        and pagination is also possible using start and count parameters, default is to return all available
        submitted forms for the period.

        :param draw: draw ID, sequental
        :param tbeg: date and time from which to select tasks
        :param tend: date and time till which to select tasks
        :param start: if given, then the indexed starting task to return from
        :param count: if given, then it is the count of tasks to return
        :return: dict with application/x-www-form-urlencoded fields
        """
        if isinstance(start, int) and isinstance(count, int):
            _start = start
            _count = count
        else:
            _start = 0
            _count = 2 ** 31 - 1
        return {"draw": str(draw),
                "columns[0][data]": r"select",
                "columns[0][name]": r"",
                "columns[0][searchable]": r"true",
                "columns[0][orderable]": r"false",
                "columns[0][search][value]": r"",
                "columns[0][search][regex]": r"false",
                "columns[1][data]": r"id",
                "columns[1][name]": r"id",
                "columns[1][searchable]": r"true",
                "columns[1][orderable]": r"true",
                "columns[1][search][value]": r"",
                "columns[1][search][regex]": r"false",
                "columns[2][data]": r"consecutive_nr",
                "columns[2][name]": r"consecutive_nr",
                "columns[2][searchable]": r"true",
                "columns[2][orderable]": r"true",
                "columns[2][search][value]": r"",
                "columns[2][search][regex]": r"false",
                "columns[3][data]": r"form\.id",
                "columns[3][name]": r"form\.id",
                "columns[3][searchable]": r"true",
                "columns[3][orderable]": r"true",
                "columns[3][search][value]": r"",
                "columns[3][search][regex]": r"false",
                "columns[4][data]": r"form\.name",
                "columns[4][name]": r"form\.name",
                "columns[4][searchable]": r"true",
                "columns[4][orderable]": r"true",
                "columns[4][search][value]": r"",
                "columns[4][search][regex]": r"false",
                "columns[4][translated]": r"true",
                "columns[4][version]": r"form_submissions.version",
                "columns[5][data]": r"site\.id",
                "columns[5][name]": r"site\.id",
                "columns[5][searchable]": r"true",
                "columns[5][orderable]": r"true",
                "columns[5][search][value]": r"",
                "columns[5][search][regex]": r"false",
                "columns[6][data]": r"site\.deleted_at",
                "columns[6][name]": r"site\.deleted_at",
                "columns[6][searchable]": r"true",
                "columns[6][orderable]": r"true",
                "columns[6][search][value]": r"",
                "columns[6][search][regex]": r"false",
                "columns[6][timestamp]": r"true",
                "columns[7][data]": r"site\.name",
                "columns[7][name]": r"site\.name",
                "columns[7][searchable]": r"true",
                "columns[7][orderable]": r"true",
                "columns[7][search][value]": r"",
                "columns[7][search][regex]": r"false",
                "columns[8][data]": r"element\.id",
                "columns[8][name]": r"element\.id",
                "columns[8][searchable]": r"true",
                "columns[8][orderable]": r"true",
                "columns[8][search][value]": r"",
                "columns[8][search][regex]": r"false",
                "columns[9][data]": r"element\.deleted_at",
                "columns[9][name]": r"element\.deleted_at",
                "columns[9][searchable]": r"true",
                "columns[9][orderable]": r"true",
                "columns[9][search][value]": r"",
                "columns[9][search][regex]": r"false",
                "columns[9][timestamp]": r"true",
                "columns[10][data]": r"element\.name",
                "columns[10][name]": r"element\.name",
                "columns[10][searchable]": r"true",
                "columns[10][orderable]": r"true",
                "columns[10][search][value]": r"",
                "columns[10][search][regex]": r"false",
                "columns[10][translated]": r"true",
                "columns[11][data]": r"employee\.deleted_at",
                "columns[11][name]": r"employee\.deleted_at",
                "columns[11][searchable]": r"true",
                "columns[11][orderable]": r"true",
                "columns[11][search][value]": r"",
                "columns[11][search][regex]": r"false",
                "columns[11][timestamp]": r"true",
                "columns[12][data]": r"employee\.contact\.name",
                "columns[12][name]": r"employee\.contact\.name",
                "columns[12][searchable]": r"true",
                "columns[12][orderable]": r"true",
                "columns[12][search][value]": r"",
                "columns[12][search][regex]": r"false",
                "columns[12][contact_name]": r"true",
                "columns[13][data]": r"user\.id",
                "columns[13][name]": r"user\.id",
                "columns[13][searchable]": r"true",
                "columns[13][orderable]": r"true",
                "columns[13][search][value]": r"",
                "columns[13][search][regex]": r"false",
                "columns[14][data]": r"user\.deleted_at",
                "columns[14][name]": r"user\.deleted_at",
                "columns[14][searchable]": r"true",
                "columns[14][orderable]": r"true",
                "columns[14][search][value]": r"",
                "columns[14][search][regex]": r"false",
                "columns[14][timestamp]": r"true",
                "columns[15][data]": r"user\.contact\.name",
                "columns[15][name]": r"user\.contact\.name",
                "columns[15][searchable]": r"true",
                "columns[15][orderable]": r"true",
                "columns[15][search][value]": r"",
                "columns[15][search][regex]": r"false",
                "columns[15][contact_name]": r"true",
                "columns[16][data]": r"created_at",
                "columns[16][name]": r"created_at",
                "columns[16][searchable]": r"true",
                "columns[16][orderable]": r"true",
                "columns[16][search][value]": r"",
                "columns[16][search][regex]": r"false",
                "columns[16][timestamp]": r"true",
                "columns[17][data]": r"url",
                "columns[17][name]": r"url",
                "columns[17][searchable]": r"true",
                "columns[17][orderable]": r"true",
                "columns[17][search][value]": r"",
                "columns[17][search][regex]": r"false",
                "columns[18][data]": r"dummy_images",
                "columns[18][name]": r"dummy_images",
                "columns[18][searchable]": r"true",
                "columns[18][orderable]": r"true",
                "columns[18][search][value]": r"",
                "columns[18][search][regex]": r"false",
                "columns[19][data]": r"displayColumns",
                "columns[19][name]": r"",
                "columns[19][searchable]": r"true",
                "columns[19][orderable]": r"false",
                "columns[19][search][value]": r"",
                "columns[19][search][regex]": r"false",
                "order[0][column]": r"1",
                "order[0][dir]": r"desc",
                "start": str(_start),
                "length": str(_count),
                "search[value]": r"",
                "search[regex]": r"false",
                "dates[from]": tbeg.strftime("%Y-%m-%d %H:%M"),
                "dates[to]": tend.strftime("%Y-%m-%d %H:%M"),
                "dateColumn": r"created_at",
                "timeColumn": r"false"
                }
