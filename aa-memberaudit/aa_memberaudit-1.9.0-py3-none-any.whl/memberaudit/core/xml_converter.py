import ast
import re

from django.utils.safestring import mark_safe
from eveuniverse.models import EveEntity

from allianceauth.eveonline.evelinks import dotlan, evewho
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from .. import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


_font_regex = re.compile(
    r'<font (?P<pre>.*?)(size="(?P<size>[0-9]{1,2})")? ?(color="#[0-9a-f]{2}(?P<color>[0-9a-f]{6})")?(?P<post>.*?)>'
)
_link_regex = re.compile(
    r'<a href="(?P<schema>[a-zA-Z]+):(?P<first_id>\d+)((//|:)(?P<second_id>[0-9a-f]+))?">'
)


def _font_replace(font_match) -> str:
    pre = font_match.group("pre")  # before the color attr
    size = font_match.group("size")
    color = font_match.group("color")  # the raw color (eg. 'ffffff')
    post = font_match.group("post")  # after the color attr

    if color is None or color == "ffffff":
        color_attr = ""
    else:
        color_attr = f"color: #{color};"
    if size is None:
        size_attr = ""
    else:
        size_attr = f"font-size: {size}pt;"
    return f'<span {pre}style="{color_attr} {size_attr}"{post}>'


def _link_replace(link_match) -> str:
    schema = link_match.group("schema")
    first_id = int(link_match.group("first_id"))
    second_id = link_match.group("second_id")
    if schema == "showinfo":
        if second_id is not None:
            second_id = int(second_id)
        if 1373 <= first_id <= 1386:  # Character
            return f'<a href="{evewho.character_url(second_id)}" target="_blank">'
        elif first_id == 5:  # Solar System
            system_name = EveEntity.objects.resolve_name(second_id)
            return f'<a href="{dotlan.solar_system_url(system_name)}" target="_blank">'
        elif first_id == 2:  # Corporation
            corp_name = EveEntity.objects.resolve_name(second_id)
            return f'<a href="{dotlan.corporation_url(corp_name)}" target="_blank">'
        elif first_id == 16159:  # Alliance
            alliance_name = EveEntity.objects.resolve_name(second_id)
            return f'<a href="{dotlan.alliance_url(alliance_name)}" target="_blank">'
    return """<a href="javascript:showInvalidError();">"""


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def eve_xml_to_html(xml: str) -> str:
    x = _font_regex.sub(_font_replace, xml)
    x = x.replace("</font>", "</span>")
    x = _link_regex.sub(_link_replace, x)
    # x = strip_tags(x)
    if is_ascii(x):
        x = bytes(x, "ascii").decode("unicode-escape")
        # temporary fix to address u-bug in ESI endpoint
        # workaround to address syntax error bug (#77)
        # TODO: remove when fixed
        if x.startswith("u'") and x.endswith("'"):
            try:
                x = ast.literal_eval(x)
            except SyntaxError:
                logger.warning("Failed to convert XML")
                x = ""

    return mark_safe(x)
