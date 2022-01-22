# -*- coding: utf-8 -*-
from __future__ import print_function
from io import StringIO
from dktemplate.parse import nest
from dktemplate.tokenize import tokenize


class Render(object):
    def __init__(self, content):
        self.content = content
        self.out = StringIO()
        self.curlevel = 0

    def value(self):
        return self.out.getvalue()

    def render(self, item=None):
        if item is None:
            item = self.content[0]

        tag = item[0]

        if tag.startswith('block:'):
            tag = 'block'

        # print '[I]', item, 'CALLING:', getattr(self, 'render_' + tag).__name__ , item
        try:
            getattr(self, 'render_' + tag)(item)
        except:  # noqa
            print('='*80)
            print(self.out.getvalue())
            raise

    def render_block(self, block):
        print("{%% %s %%}" % block[0], file=self.out)
        if len(block) > 1:
            for item in block[1]:
                self.render(item)
        print("{%% end%s %%}" % block[0], file=self.out)

    def render_tag(self, tag):
        print("{%% %s %%}" % (' '.join(tag[1:])), file=self.out)

    def render_val(self, item):
        print("{{ %s }}" % item[1], file=self.out)


def render(txt, fname=None):
    item = [nest(tokenize(txt), fname)]
    r = Render("")
    r.render(item)
    return r.value()
