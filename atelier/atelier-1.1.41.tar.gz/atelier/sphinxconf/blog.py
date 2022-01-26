# -*- coding: utf-8 -*-
# Copyright 2011-2021 Rumma & Ko Ltd.
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""This Sphinx extension defines the :rst:dir:`blogger_year` and
:rst:dir:`blogger_index` directives.

Usage: add the following to your `conf.py`::

  extensions += ['atelier.sphinxconf.blog']

And usually this file structure:

- docs/blog/index.rst --> contains a main_blogindex directive (hidden toctree)

Individual blog entries are automatically created by :cmd:`inv blog`,
leading to a file structure like this:

- docs/blog/2013/index.rst --> contains a :rst:dir:`blogger_year` directive
- docs/blog/2013/0107.rst --> a blog entry
- docs/blog/2013/0108.rst --> another blog entry
- docs/blog/2013/0108b.rst --> a second blog entry on January 8

The  :cmd:`inv blog` command automatically creates yearly directories and
`index.rst` files when needed.

If you want a second separate blog entry on a same day, you must manually create
a file.


Thanks to

- `Creating reStructuredText Directives
  <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_

"""

import os
import calendar
import datetime

from sphinx.directives.other import Author


import jinja2

from babel.dates import format_date

from .insert_input import InsertInputDirective
from rstgen import toctree


def monthname(n, language):
    """
    Return the monthname for month # n in specified language.
    """
    d = datetime.date(2013, n, 1)
    return format_date(d, "MMMM", locale=language)


templates = dict()
templates['calendar.rst'] = """
====
{{year}}
====

{{intro}}

.. |br| raw:: html

   <br />

.. |sp| raw:: html

   <span style="color:white;">00</span>

{{calendar}}


"""

JINJA_ENV = jinja2.Environment(
    #~ extensions=['jinja2.ext.i18n'],
    loader=jinja2.DictLoader(templates))


class BloggerDay(object):
    def __init__(self, *args, **kwargs):
        self.docnames = []
        self.date = datetime.date(*args, **kwargs)


class BloggerYear(object):

    """A :class:`BloggerYear` instance is created for each `blogger_year`
    directive.

    """

    def __init__(self, env):
        """
        :docname: the name of the document containing the `main_blogindex` directive
        :starting_year: all years before this year will be pruned
        """

        blogname, year, index = env.docname.rsplit('/', 3)
        if index != 'index':
            raise Exception(
                "Allowed only in /<blogname>/<year>/index.rst files")
        self.blogname = blogname
        self.year = int(year)

        #~ print "20130113 Year.__init__", blogname, self.year
        #~ self.blogname = blogname
        self.days = []
        self.dates = {}
        #~ self.years = set()
        #~ self.starting_year = int(starting_year)
        top = os.path.dirname(env.doc2path(env.docname))
        #~ print top
        # print("20211021", year, top, getattr(env, 'blog_instances', None))
        for (dirpath, dirnames, filenames) in os.walk(top):
            del dirnames[:]  # don't descend another level
            #~ unused, year = dirpath.rsplit(os.path.sep,2)
            #~ year = int(year)
            #~ assert year in self.years
            currentday = None
            docnames = sorted([fn[:-4] for fn in filenames if fn.endswith('.rst')])
            for docname in sorted(docnames):
                if docname == "index":
                    continue
                d = self.docname_to_day(docname, currentday)
                if d is not None:
                    dates_item = self.dates.get(d.date, None)
                    if dates_item is None:
                        self.dates[d.date] = d
                    # self.dates.add(d.date)
                    currentday = d

        #~ self.years = sorted(self.years)
        if not hasattr(env, 'blog_instances'):
            env.blog_instances = dict()
        years = env.blog_instances.setdefault(blogname, dict())
        years[self.year] = self
        # print("20211021b", year, top, env.blog_instances)

    def docname_to_day(self, s, currentday):
        if len(s) < 4:
            return None
        try:
            month = int(s[:2])
            day = int(s[2:4])
        except ValueError:
            return None
        if currentday is None or currentday.date.month != month \
            or currentday.date.day != day:
                currentday = BloggerDay(self.year, month, day)
                self.days.append(currentday)
        currentday.docnames.append(s)
        return currentday


def year2docname(y):
    assert isinstance(y, BloggerYear)
    return "/" + y.blogname + "/" + str(y.year) + "/index"


def navigator(years, current):
    """`years` is an iterable of :class:`BloggerYear` instances.
    """
    # if len(years) < 2:
    #     return ""
    chunks = []
    for y in years:
        if y == current:
            chunks.append(str(y.year))
        else:
            chunks.append(
                ":doc:`{0} <{1}>`".format(y.year, year2docname(y)))
    old = ' '.join(chunks)
    return "\n\n{0}\n\n".format(old)


def get_all_entries(env):

    blog_instances = getattr(env, 'blog_instances', dict())
    entries = []
    for blogname, blog in blog_instances.items():
        for year in blog.values():
            for day in year.days:
                for docname in day.docnames:
                    entries.append((day.date, blogname, year.year, docname))

    #     years.sort(key=lambda f: f.year)
    #
    # years = get_blogger_years(env, blogname)
    # years = reversed(years, key=lambda f: f.year)
    entries.sort(key=lambda e: e[0])
    return reversed(entries)


def get_blogger_years(env, blogname):
    blog_instances = getattr(env, 'blog_instances', dict())
    blog = blog_instances.get(blogname)
    if blog is None:
        return []
    years = list(blog.values())
    years.sort(key=lambda f: f.year)
    # print(20220109, [y.year for y in years])
    return years


class MainBlogIndexDirective(InsertInputDirective):
    """
    Directive to insert a blog master archive page toctree
    """
    # required_arguments = 1
    # allow_titles = True
    raw_insert = True

    def get_rst(self):
        env = self.state.document.settings.env
        blogname, index = env.docname.rsplit('/', 2)
        if index != 'index':
            raise Exception("Allowed only inside index.rst file")
        text = ''
        years = get_blogger_years(env, blogname)
        # print('20211021 MainBlogIndexDirective.get_rst()', years)
        text += navigator(years, None)
        text += '\n'.join(self.content)
        if len(years) == 0:
            text += "\n\nNo blogger years found.\n"
        else:
            children = list(map(year2docname, years))
            text += toctree(*children, hidden=True)
        # print('20211021b get_rst()', text)
        return text

class YearBlogIndexDirective(InsertInputDirective):

    """
    Directive to insert a year's calendar
    """
    #~ required_arguments = 1
    #~ allow_titles = True
    raw_insert = True

    def get_rst(self):

        env = self.state.document.settings.env
        today = datetime.date.today()

        blogger_year = BloggerYear(env)
        years = get_blogger_years(env, blogger_year.blogname)
        tpl = JINJA_ENV.get_template('calendar.rst')

        intro = navigator(years, blogger_year)
        intro += '\n'.join(self.content)

        text = ''
        cal = calendar.Calendar()
        num_entries = 0
        for month in range(1, 13):

            text += """

.. |M%02d| replace::  **%s**""" % (month, monthname(month, self.language))

            weeknum = None
            #~ text += "\n  |br| Mo Tu We Th Fr Sa Su "
            for day in cal.itermonthdates(blogger_year.year, month):
                iso_year, iso_week, iso_day = day.isocalendar()
                if iso_week != weeknum:
                    text += "\n  |br|"
                    weeknum = iso_week
                if day.month == month:
                    label = "%02d" % day.day
                    # docname = "%02d%02d" % (day.month, day.day)
                    # if blogger_year.year == iso_year and day in blogger_year.days:
                    blogday = blogger_year.dates.get(day, None)
                    if blogday is not None:
                        docname = blogday.docnames[0]
                        text += " :doc:`%s <%s>` " % (label, docname)
                        num_entries += 1
                    elif day > today:
                        text += ' |sp| '
                    else:
                        text += ' ' + label + ' '
                else:
                    text += ' |sp| '

        if num_entries > 8:
            text += """

===== ===== =====
|M01| |M02| |M03|
|M04| |M05| |M06|
|M07| |M08| |M09|
|M10| |M11| |M12|
===== ===== =====

.. rubric:: {0}""".format("All entries:")

        text += "\n\n"

        days = blogger_year.days
        if False:
            days = reversed(days)

        for day in days:
            date_text = format_date(day.date, format="long", locale=self.language).strip()
            text += ("\n\n**{}** --- ".format(date_text))
            text += ", ".join([":doc:`{}`".format(docname) for docname in day.docnames])

        text += """

.. toctree::
    :hidden:

"""

        for day in blogger_year.days:
            for docname in day.docnames:
                text += ("\n    " + docname)
    #         text += """
    # %02d%02d""" % (day.month, day.day)

        retval = tpl.render(
            calendar=text,
            intro=intro,
            year=blogger_year.year)
            # days=blogger_year.days)
        # print("="*80)
        # print(retval)
        # print("="*80)
        return retval


class LatestEntriesDirective(InsertInputDirective):
    """
    Directive to insert a list of the latest blog entries.
    """
    # required_arguments = 1
    # allow_titles = True
    raw_insert = True
    has_content = False

    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        env = self.state.document.settings.env
        # blogname, index = env.docname.rsplit('/', 2)
        # if index != 'index':
        #     raise Exception("Allowed only inside index.rst file")
        text = ''
        # text += '\n'.join(self.content)
        max_count = 10
        for i, e in enumerate(get_all_entries(env)):
            text += '- {0} :doc:`{1}/{2}/{3}`\n'.format(*e)
            if i == max_count:
                break
        if len(text) == 0:
            text += "\n\nNo blog entries found.\n"
        return text


def setup(app):
    #~ app.add_node(blogindex)
    #~ app.add_node(blogindex,html=(visit_blogindex,depart_blogindex))
    #~ app.add_directive('changed', ChangedDirective)
    # app.add_config_value('blog_instances', dict(), '')
    app.add_directive('blogger_year', YearBlogIndexDirective)
    app.add_directive('blogger_index', MainBlogIndexDirective)
    app.add_directive('blogger_latest', LatestEntriesDirective)
    app.add_directive('blogauthor', Author)
