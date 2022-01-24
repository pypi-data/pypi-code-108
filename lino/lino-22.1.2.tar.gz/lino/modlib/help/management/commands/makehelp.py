# -*- coding: UTF-8 -*-
# Copyright 2011-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import logging
logger = logging.getLogger(__name__)

import os
import sys
import tempfile
import subprocess
from optparse import make_option
from os.path import join, exists
from io import open
from pathlib import Path

from django.db import models
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.encoding import force_str
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from django.apps import apps

import atelier
from atelier.projects import Project

import lino
#from lino.core.utils import app_labels
from lino.utils import curry
import rstgen
from atelier.utils import cd
from lino.utils.restify import doc2rst, abstract
from lino.core import kernel
from lino.core import actors
from lino.core import fields
from lino.core import elems
from lino.core.boundaction import BoundAction
from lino.core.tables import AbstractTable
from lino.core.model import Model
from lino.core.utils import model_class_path
from lino.modlib.help.utils import HelpTextsLoader, simplify_name
from lino.modlib.gfks.fields import GenericForeignKey
from lino.api.dd import full_model_name
from lino.api import doctest

use_dirhtml = False

include_useless = False

def runcmd(cmd, **kw):
    """Run the specified command in a subprocess.

    Stop when Ctrl-C. If the subprocess has non-zero return code, we simply
    stop. We don't use check=True because this would add another useless
    traceback.  The subprocess is responsible for reporting the reason of
    the error.

    """
    # kw.update(stdout=subprocess.PIPE)
    # kw.update(stderr=subprocess.STDOUT)
    kw.update(shell=True)
    kw.update(universal_newlines=True)
    cp = subprocess.run(cmd, **kw)
    if cp.returncode != 0:
        # subprocess.run("sudo journalctl -xe", **kw)
        raise Exception(
        "{} ended with return code {}".format(cmd, cp.returncode))



def field_ref(f):
    if isinstance(f.model, Model):
        return ":ref:`{}.{}`".format(full_model_name(f.model), f.name)
    # parameter field
    return ":ref:`{}.{}`".format(str(f.model), f.name)

def report_ref(rpt):
    return ":doc:`{}`".format(str(rpt))
    # return settings.SITE.server_url + '.' + str(rpt)
    #~ return ":ref:`%s.%s`" % (settings.SITE.source_name,str(rpt))

def model_ref(model):
    return settings.SITE.source_name + '.' + model._meta.app_label + '.' + model.__name__

def verbose_name(f):
    return str(f.verbose_name or "(None)")

def shortpar(name='', label='', text=''):
    label = str(label).strip() or _("(no label)")
    text = str(text).strip()
    name = str(name).strip()
    return doc2rst(f"**{label}** ({name}) : {text}")

def rubric(s):
    return "\n\n.. rubric:: {}\n\n".format(s)

def rptlist(l):
    return ', '.join([report_ref(rpt) for rpt in sorted(l, key=str)])
        # ":doc:`%s (%s) <%s>`" % (str(rpt),
        #                          force_str(rpt.label), report_ref(rpt))
        # for rpt in l])

def model_referenced_from(model):
    #~ headers = ["name","description"]
    #~ rows = []
    def ddhfmt(ddh):
        return ', '.join(['{}.{}'.format(full_model_name(model), fk.name)
                          for model, fk in ddh.fklist])
    return ddhfmt(model._lino_ddh)
    #~ rows.append(['_lino_ddh',ddhfmt(model._lino_ddh)])
    #~ return rstgen.table(headers,rows)


class GeneratingCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-t', '--tmpdir', action='store',
                            dest='tmpdir', default=None,
                            help='Path for temporary files.')
        parser.add_argument('-l', '--language', action='store',
                            dest='language', default=None,
                            help='Generate only the specified language.')

    def handle(self, *args, **options):

        self.options = options
        parts = ('cache', 'help')
        self.output_dir = join(settings.SITE.site_cache_root, *parts)
        self.generated_count = 0
        self.htl = HelpTextsLoader(settings.SITE)

        tmpdir = options['tmpdir']
        if tmpdir:
            self.run_on_temp_dir(tmpdir)
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                self.run_on_temp_dir(tmpdirname)

    def run_on_temp_dir(self, temp_dir):
        verbosity = self.options.get('verbosity', 0)
        self.temp_dir = temp_dir
        logger.info("Generate temporary rst files to %s", self.temp_dir)

        self.generate_files()
        logger.info("Generated %s files to %s", self.generated_count, self.temp_dir)
        logger.info("Building site help html to %s", self.output_dir)

        def doit(lng):
            self.language = lng
            docs_dir = self.docspath()
            builder = 'html'
            if use_dirhtml:
                builder = 'dirhtml'
            args = ['sphinx-build', '-b', builder]
            args += ['-T'] # show full traceback on exception
            # ~ args += ['-a'] # all files, not only outdated
            # ~ args += ['-P'] # no postmortem
            if not verbosity:
                args += ['-Q'] # no output
            args += ['.']
            if lng.index == 0:
                args += [self.output_dir]
            else:
                args += [join(self.output_dir, lng.django_code)]
            cmd = ' '.join(args)
            print("Run `cd {} && {}`".format(docs_dir, cmd))
            with cd(docs_dir):
                runcmd(cmd)

        self.with_languages(doit)


    def docspath(self, output_file=None):
        parts = [self.temp_dir]
        if self.language.index == 0:
            parts.append('docs')
        else:
            parts.append(self.language.django_code + 'docs')
        if output_file:
            parts.append(output_file)
        return os.path.join(*parts)

    def generate(self, tplname, output_file, **context):
        output_file = self.docspath(output_file)
        logger.info("Generating %s", output_file)
        #~ logger.info("Generating %s from %s",fn,tpl_filename)
        env = settings.SITE.plugins.jinja.renderer.jinja_env
        template = env.get_template(tplname)
        context.update(self.context)
        content = template.render(**context)
        open(output_file, 'wt').write(content)
        self.generated_count += 1
        return ''


class Command(GeneratingCommand):
    help = "Generate the local help pages for this Lino site."

    def generate_files(self):

        self.context = dict(
            header=rstgen.header,
            h1=curry(rstgen.header, 1),
            table=rstgen.table,
            doc2rst=doc2rst,
            models=models,
            abstract=abstract,
            refto=self.refto,
            settings=settings,
            actors=actors,
            # actors_list=[a for a in actors.actors_list if not a.abstract],
            doctest=doctest,
            translation=translation,
            use_dirhtml=use_dirhtml,
            include_useless=include_useless,
            #~ py2rst=rstgen.py2rst,
            languages=[lng.django_code for lng in settings.SITE.languages],
            get_models=apps.get_models,
            full_model_name=full_model_name,
            model_overview=self.model_overview,
            actor2par=self.actor2par,
            actors2table=self.actors2table,
            plugin_overview=self.plugin_overview,
            actor_overview=self.actor_overview,
            model_referenced_from=model_referenced_from,
            model_ref=model_ref,
            makedocs=self,
        )
        self.context['_'] = _

        def doit(lng):
            self.language = lng
            os.makedirs(self.docspath(), exist_ok=True)
            self.generate('makedocs/conf.tpl.py', 'conf.py')
            self.generate('makedocs/index.tpl.rst', 'index.rst')
            self.generate('makedocs/actors.tpl.rst', 'actors.rst')
            if include_useless:
                self.generate('makedocs/models.tpl.rst', 'models.rst')
                self.generate('makedocs/plugins.tpl.rst', 'plugins.rst')

        self.with_languages(doit)

    def with_languages(self, doit):
        lng = self.options.get('language', None)
        if lng is None:
            for lng in settings.SITE.languages:
                doit(lng)
        else:
            lng = settings.SITE.get_language_info(lng)
            doit(lng)

    def refto(self, x, text=None):
        if x is None:
            return '`None`'
        if isinstance(x, type):
            if issubclass(x, actors.Actor):
                if text is None: text = str(x)
                ref = self.get_help_text_ref(x)
                if ref:
                    return ':class:`{} <{}>`'.format(text, ref)
            elif issubclass(x, models.Model):
                if text is None: text = x.__name__
                return ':doc:`' + text + ' <' + full_model_name(x) + '>`'
        if isinstance(x, BoundAction):
            if text is None: text = x.action_name
            return ':doc:`{} <{}>`'.format(text, x.actor)
        if isinstance(x, (models.Field, fields.FakeField, GenericForeignKey)):
            if text is None: text = x.verbose_name or x.name
            ref = self.get_help_text_ref(x)
            if ref:
                return ':attr:`{} <{}>`'.format(text, ref)
            if getattr(x, 'model', None):
                ref = simplify_name(model_class_path(x.model))
                return ':attr:`{} <{}.{}>`'.format(text, ref, x.name)
            return ':attr:`{} <oops>`'.format(x.name)
        return "(unformatted: ``{}``)".format(repr(x))
        #~ if isinstance(x,Field):
        # return ':ref:`' + x.verbose_name + ' <' + full_model_name(x.model) + '.' + x.name + '>`'

    def get_help_text_ref(self, x):
        ref = getattr(x, '_lino_help_ref', None)
        if ref:
            return ref
        if not isinstance(x, type):
            x = x.__class__
        for cls in x.mro():
            ref, txt = self.htl.get_help_text_for_class(cls)
            # ref = getattr(cls, '_lino_help_ref', None)
            if txt:
                return ref

    def fieldtype(self, f):
        if isinstance(f, models.ForeignKey):
            return f.__class__.__name__ + " to " + self.refto(f.remote_field.model)
        return f.__class__.__name__

    def get_help_text_from_field(self, f):
        # if isinstance(f, elems.FieldElement):
        #     f = f.field
        if f.help_text:
            return f.help_text
        return "See {}.".format(self.refto(f))

    def field2par(self, f):
        return shortpar(f.name, verbose_name(f), self.get_help_text_from_field(f))

    def elem2par(self, e):
        if isinstance(e, elems.Panel):
            return rstgen.ul([self.elem2par(e) for e in e.elements])
        if isinstance(e, elems.GridElement):
            # return report_ref(e.actor)
            rpt = e.actor
            if rpt.label:
                return "**{}** (:doc:`{} <{}>`)".format(rpt.label, str(rpt), str(rpt))
            # return shortpar(refto(e.actor, e.name), e.verbose_name, self.get_help_text_from_field(e))
        if isinstance(e, elems.FieldElement):
            e = e.field
        if isinstance(e, (models.Field, fields.FakeField, GenericForeignKey)):
            return shortpar(self.refto(e, e.name), e.verbose_name, self.get_help_text_from_field(e))
        return self.refto(e)

    def actors2table(self):
        rows = []
        headers = [_("Name"), _("Description")]
        for a in actors.actors_list:
            if a.abstract: continue
            ref, text = self.htl.get_help_text_for_class(a)
            label = ":doc:`{} <{}>`".format(a.label, a)
            name = ":class:`{} <{}>`".format(a, ref)
            title = "{} ({})".format(label, name)
            rows.append([title, text])
        return rstgen.table(headers, rows)

    def actor2par(self, a):
        ref, text = self.htl.get_help_text_for_class(a)
        label = ":doc:`{}`".format(a)
        name = ":class:`{} <{}>`".format(a, ref)
        return "".format(name, label, text)

    def action2par(self, a):
        if isinstance(a, BoundAction):
            a = a.action
        return shortpar(a.action_name, a.label, self.get_help_text_from_field(a))

    def collect_refs(self, cls, role):
        refs = []
        if cls is None: return refs
        for i, b in enumerate(cls.mro()):
            if i == 0:
                continue
            ref = self.get_help_text_ref(b)
            if ref and not ref in refs:
                refs.append(ref)
        return [':{}:`{}`'.format(role, ref) for ref in refs]

    def get_intro(self, cls):
        s = ""
        ref, txt = self.htl.get_help_text_for_class(cls)

        if txt:
            s += "\n\n" + str(txt)
            s += " :class:`{} <{}>`".format(_("(more)"), ref)
        else:
            s += "\n\n" + _("No help_text for {}").format(cls)

        refs = self.collect_refs(cls, "class")
        # refs += self.collect_refs(rpt.model, "class")
        if len(refs):
            s += "\n\n" + _("Inherits from") + " " + ", ".join(refs)
        return s

    def actor_overview(self, rpt):
        # if issubclass(rpt, AbstractTable):
        s = self.get_intro(rpt)

        if rpt.model:
            m = rpt.model
            row_ref = self.get_help_text_ref(m)
            if issubclass(m, models.Model):
                row_label = _("a :class:`{} <{}>`").format(
                    m._meta.verbose_name, row_ref)
                # s += "\n\n**{}** : {}".format(
                #     _("Database model"), self.refto(m, full_model_name(m)))
            else:
                row_label = _("an instance of :class:`{} <{}>`").format(
                    simplify_name(model_class_path(m)), row_ref
                )
                # s += "\n\n**{}** : {}".format(
                #     _("Row model"), self.refto(m))
            msg = _("Every row of this :term:`data view` is {}.")
            s += "\n\n" + msg.format(row_label, row_ref)

        msg = _("User Guide: :ref:`ug.plugins.{}`.")
        s += "\n\n" + msg.format(rpt.app_label)

        seen = set()

        def show(title, elems):
            s = rubric(title)
            s += rstgen.ul([self.elem2par(e) for e in elems])
            seen.update(elems)
            return s

        visible = []
        hidden = []
        if not rpt.is_abstract():
            if issubclass(rpt, AbstractTable):
                for e in rpt.get_handle().get_columns():
                    if e.hidden:
                        hidden.append(e)
                    else:
                        visible.append(e)
                # s += show(_("Columns"), rpt.get_handle().get_columns())
                s += show(_("Columns"), visible)
            # s += rubric(_("Columns"))
            # s += rstgen.ul([elem2par(e) for e in rpt.list_layout.walk()])
            # s += rstgen.ul([elem2par(f) for f in rpt.wildcard_data_elems()])

        # s += show(_("Other fields"),
        #     [e for e in rpt.wildcard_data_elems() if not e in seen])


        if rpt.detail_action:
            s += show(_("Detail layout"), rpt.get_detail_elems())
            # s += rubric(_("Detail fields"))
            # s += rstgen.ul([elem2par(f) for f in rpt.get_detail_elems()])

        s += rubric(_("Toolbar actions"))
        # s += rstgen.ul([action2par(a) for a in rpt.get_toolbar_actions()])
        s += rstgen.ul([self.action2par(ba) for ba in rpt._actions_list if ba.action.show_in_bbar])
        if rpt.parameters:
            s += show(_("Filter parameters"), rpt.parameters.values())
            # s += rubric(_("Filter parameters"))
            # s += rstgen.ul([elem2par(f) for f in rpt.parameters.values()])
        if len(hidden):
            s += show(_("Hidden columns"), hidden)
        return s

    def model_overview(self, model):
        s = self.get_intro(model)
        masters = [r for r in kernel.master_tables if r.model is model]
        if masters:
            s += "\n\n**{}** : {}".format(_("Master tables"), rptlist(masters))
        slaves = getattr(model, '_lino_slaves', None)
        if slaves:
            s += "\n\n**{}** : {}".format(_("Slave tables"), rptlist(slaves.values()))

        pointers = []
        for fm, fk in model._lino_ddh.fklist:
            pointers.append(self.refto(fk))
        if len(pointers):
            s += "\n\n**{}** : {}".format(_("Pointers"), ', '.join(pointers))

        # s += rubric("Database fields:")
        # s += rstgen.ul([self.field2par(f) for f in model._meta.fields])
        return s

    def plugin_overview(self, plugin):
        s = self.get_intro(plugin.__class__)
        return s
