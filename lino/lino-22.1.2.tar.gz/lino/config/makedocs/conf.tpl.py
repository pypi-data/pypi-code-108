# -*- coding: utf-8 -*-
from pathlib import Path

{% if makedocs.language.index == 0 %}

html_context = dict(public_url="{{settings.SITE.server_url}}media/cache/help")
from atelier.projects import add_project
prj = add_project('..')
prj.SETUP_INFO = dict()
prj.config.update(use_dirhtml={{use_dirhtml}})
prj.config.update(selectable_languages={{languages}})

from lino.sphinxcontrib import configure ; configure(globals(), project=prj)

# print("20210525", prj, html_context)

project = "{{settings.SITE.title}}"
html_title = "{{settings.SITE.title}}"
copyright = '2019-2021 Rumma & Ko Ltd'
htmlhelp_basename = 'help'
extensions += ['lino.sphinxcontrib.logo']

# from atelier.sphinxconf import interproject
# interproject.configure(globals())

{% else %}

docs = Path('../docs').resolve()
fn = docs / 'conf.py'
with open(fn, "rb") as fd:
    exec(compile(fd.read(), fn, 'exec'))

{% endif %}

language = '{{makedocs.language.django_code}}'
