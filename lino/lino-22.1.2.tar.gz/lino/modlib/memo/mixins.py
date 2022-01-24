# -*- coding: UTF-8 -*-
# Copyright 2016-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import html as lxml_html
from etgen.html import E, tostring
import lxml

from django.conf import settings
from django.utils import translation

from lino.core.model import Model
from lino.core.requests import BaseRequest
from lino.core.fields import fields_list, RichTextField, PreviewTextField
from lino.utils.restify import restify
from lino.utils.mldbc.fields import BabelTextField
from lino.core.exceptions import ChangedAPI
from lino.modlib.checkdata.choicelists import Checker
from lino.api import _


def truncate_comment(html_str, max_p_len=300):
    html_str = html_str.strip()  # remove leading or trailing newlines

    if not html_str.startswith('<'):
        if len(html_str) > max_p_len:
            txt = html_str[:max_p_len] + "..."
        else:
            txt = html_str
        return txt
    soup = BeautifulSoup(html_str, "html.parser")
    ps = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "pre"])
    if len(ps) > 0:
        anchor_end = '</a>'
        txt = ""
        for p in ps:
            text = ""
            for c in p.contents:
                if isinstance(c, Tag):
                    if c.name == 'a':
                        text += str(c)
                        max_p_len = max_p_len + len(text) - len(c.text)
                    else:
                        text += c.text
                else:
                    text += str(c)

            if len(txt) + len(text) > max_p_len:
                txt += text
                if anchor_end in txt:
                     ae_index = txt.index(anchor_end) + len(anchor_end)
                     if ae_index >= max_p_len:
                         txt = txt[:ae_index]
                         txt += "..."
                         break
                txt = txt[:max_p_len]
                txt += "..."
                break
            else:
                txt += text + "\n\n"
        return txt
    return html_str


def rich_text_to_elems(ar, description):
    if description.startswith("<"):
        # desc = E.raw('<div>%s</div>' % self.description)
        desc = lxml_html.fragments_fromstring(ar.parse_memo(description))
        return desc
    # desc = E.raw('<div>%s</div>' % self.description)
    html = restify(ar.parse_memo(description))
    # logger.info(u"20180320 restify %s --> %s", description, html)
    # html = html.strip()
    try:
        desc = lxml_html.fragments_fromstring(html)
    except Exception as e:
        raise Exception(
            "Could not parse {!r} : {}".format(html, e))
    # logger.info(
    #     "20160704c parsed --> %s", tostring(desc))
    return desc
    # if desc.tag == 'body':
    #     # happens if it contains more than one paragraph
    #     return list(desc)  # .children
    # return [desc]

def body_subject_to_elems(ar, title, description):
    if description:
        elems = [E.p(E.b(title), E.br())]
        elems += rich_text_to_elems(ar, description)

    else:
        elems = [E.b(title)]
        # return E.span(self.title)
    return elems

def parse_previews(source, ar=None):
    front_end = settings.SITE.plugins.memo.front_end or settings.SITE.default_ui
    if ar is None or ar.renderer.front_end is not front_end:
        ar = BaseRequest(renderer=front_end.renderer)
        # print("20190926 using BaseRequest with front end {}".format(front_end))
    parse = settings.SITE.plugins.memo.parser.parse
    full = parse(source, ar)
    short = truncate_comment(full)
    return (short, full)

class BasePreviewable(Model):
    class Meta:
        abstract = True

    previewable_field = None

    def before_ui_save(self, ar, cw):
        """Updates the preview fields from the source field.

        """
        super(BasePreviewable, self).before_ui_save(ar, cw)
        short, full = parse_previews(getattr(self, self.previewable_field), ar)
        setattr(self, self.previewable_field + '_short_preview', short)
        setattr(self, self.previewable_field + '_full_preview', full)

    def get_overview_elems(self, ar):
        yield E.h1(str(self))

        if self.body_short_preview:
            try:
                for e in lxml.html.fragments_fromstring(self.body_short_preview):
                    yield e
            except Exception as e:
                yield "{} [{}]".format(self.body_short_preview, e)




class Previewable(BasePreviewable):

    class Meta:
        abstract = True

    previewable_field = 'body'

    body = PreviewTextField(_("Body"), blank=True, format='html', bleached=True)
    body_short_preview = RichTextField(_("Preview"), blank=True, editable=False)
    body_full_preview = RichTextField(_("Preview (full)"), blank=True, editable=False)


class BabelPreviewable(BasePreviewable):

    class Meta:
        abstract = True

    previewable_field = 'body'

    body = BabelTextField(_("Body"), blank=True, format='html', bleached=True)
    body_short_preview = BabelTextField(_("Preview"), blank=True, editable=False)
    body_full_preview = BabelTextField(_("Preview (full)"), blank=True, editable=False)

    def before_ui_save(self, ar, cw):
        super(BabelPreviewable, self).before_ui_save(ar, cw)
        pf = self.previewable_field
        # short, full = parse_previews(getattr(self, pf), ar)
        # setattr(self, pf + '_short_preview', short)
        # setattr(self, pf + '_full_preview', full)
        for lng in settings.SITE.BABEL_LANGS:
            with translation.override(lng.django_code):
                src = getattr(self, self.previewable_field+lng.suffix)
                short, full = parse_previews(src, ar)
            setattr(self, pf+'_short_preview'+lng.suffix, short)
            setattr(self, pf+'_full_preview'+lng.suffix, full)


class PreviewableChecker(Checker):
    verbose_name = _("Check for previewables needing update")
    model = BasePreviewable

    def _get_checkdata_problems(self, suffix, obj, fix=False):
        pf = obj.previewable_field
        src = getattr(obj, pf+suffix)
        short, full = parse_previews(src)
        if getattr(obj, pf+'_short_preview'+suffix) != short \
            or getattr(obj, pf+'_full_preview'+suffix) != full:
            yield (True, _("Preview differs from source."))
            if fix:
                setattr(obj, pf+'_short_preview'+suffix, short)
                setattr(obj, pf+'_full_preview'+suffix, full)
                obj.full_clean()
                obj.save()

    def get_checkdata_problems(self, obj, fix=False):
        for x in self._get_checkdata_problems('', obj, fix):
            yield x
        if isinstance(obj, BabelPreviewable):
            for lng in settings.SITE.BABEL_LANGS:
                with translation.override(lng.django_code):
                    for x in self._get_checkdata_problems(lng.suffix, obj, fix):
                        yield x

PreviewableChecker.activate()
