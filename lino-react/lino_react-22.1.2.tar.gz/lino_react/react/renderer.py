# -*- coding: UTF-8 -*-
# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from html import escape
from os import path
from django.conf import settings
from django.db import models
from django.utils.text import format_lazy
from django.utils import translation

from lino.core import constants as ext_requests
from lino.core.renderer import add_user_language, JsRenderer, HtmlRenderer
from lino.core.renderer_mixins import JsCacheRenderer

from lino.core.menus import Menu, MenuItem
from lino.core import constants
from lino.core import choicelists
from lino.core.gfks import ContentType
from lino.modlib.extjs.ext_renderer import ExtRenderer

from lino.core.actions import (ShowEmptyTable, ShowDetail, WrappedAction,
                               ShowInsert, ShowTable, SubmitDetail,
                               SubmitInsert, Action)
from lino.core.boundaction import BoundAction
from lino.core.choicelists import ChoiceListMeta
from lino.modlib.system.choicelists import DashboardLayouts
from lino.core.actors import Actor
from lino.core.layouts import LayoutHandle, BaseLayout
from lino.core.elems import LayoutElement, ComboFieldElement, SimpleRemoteComboFieldElement, FieldElement
from lino.core import kernel

from etgen.html import E

from lino.utils import jsgen
from lino.utils.jsgen import py2js, js_code, obj2dict

from lino.modlib.users.utils import get_user_profile, with_user_profile

from inspect import isclass

from .icons import REACT_ICON_MAPPING


def find(itter, target, key=None):
    """Returns the index of an element in a callable which can be use a key function"""
    assert key == None or callable(key), "key shold be a function that takes the itter's item " \
                                         "and returns that wanted matched item"
    for i, x in enumerate(itter):
        if key:
            x = key(x)
        if x == target:
            return i
    else:
        return -1


class Renderer(JsRenderer, JsCacheRenderer):
    """.
        An JS renderer that uses the react Javascript framework.
    """
    is_interactive = True
    can_auth = True

    lino_web_template = "react/linoweb.json"
    file_type = '.json'
    support_dashboard_layout = True  # Used to prevent any dashboard items being rendered from main html dashboard.

    def __init__(self, front_end):
        JsRenderer.__init__(self, front_end)
        JsCacheRenderer.__init__(self)
        jsgen.register_converter(self.py2js_converter)

    def write_lino_js(self, f):
        """
        Creates what is known as window.App.state.site_data in React code.

        :param f: File object
        :return: 1
        """
        choicelists_data = {
            # ID: [{"value": py2js(c[0]).strip('"'), "text": py2js(c[1]).strip('"')} for c in cl.get_choices()] for
            ID: [{"value": c[0].value, "text": str(c[1])} for c in cl.get_choices()]
                for ID, cl in kernel.CHOICELISTS.items()}

        actions = set()
        for rpt in self.actors_list:
            # rh = rpt.get_handle() #for getting bound actor, not needed.
            for ba in rpt.get_actions():
                if ba.action not in actions:
                    actions.add(ba.action)

        self.serialise_js_code = True
        plugins = settings.SITE.plugins
        data = dict(
            actions={a.action_name: self.action2json(a) for a in actions},
            # actors={a.actor_id: a for a in self.actors_list},
            menu=settings.SITE.get_site_menu(get_user_profile()),
            suggestors=list(plugins.memo.parser.suggesters.keys()),  # [#,@] keytriggers
            use_dashboard_layouts=plugins.system.use_dashboard_layouts,
            site_title=settings.SITE.title,
            )

        if settings.SITE.never_build_site_cache:
            data.update(revision_number=settings.SITE.kernel.lino_version)
        else:
            data.update(revision_number=settings.SITE.kernel.code_mtime)

        if hasattr(settings.SITE, 'theme_name'):
            data.update(theme_name=settings.SITE.theme_name)

        if settings.SITE.user_model == None:
            data.update(no_user_model=True)
        elif hasattr(plugins.users, 'allow_online_registration'):
            data.update(allow_online_registration=plugins.users.allow_online_registration)

        if settings.SITE.is_installed('notify'):
            data.update(use_push_api=plugins.notify.use_push_api)

        # data.update(actors={str(a): a for a in self.actors_list})
        # data.update(action_param_panels={
        #     str(p): self.panel2json(p)
        #         for p in self.action_param_panels })
        # data.update(param_panels={
        #     str(p): self.panel2json(p)
        #         for p in self.param_panels })
        form_panels = {}
        for p in self.form_panels:
            form_panels[p._formpanel_name] = self.panel2json(p)
            if hasattr(p, 'choice_name') and 'system.Dashboard' in p._formpanel_name:
                for i, item in enumerate(choicelists_data['system.DashboardLayouts']):
                    if item['value'] == p.choice_name:
                        choicelists_data['system.DashboardLayouts'][i]['window_layout'] = p._formpanel_name
        for p in self.param_panels:
            form_panels[p._formpanel_name] = self.panel2json(p)
        for p in self.action_param_panels:
            form_panels[p._formpanel_name] = self.panel2json(p)
        for p in self.other_panels:
            form_panels[p._formpanel_name] = self.panel2json(p)
        data.update(form_panels=form_panels, choicelists=choicelists_data)


        # print("20210417", data)

        f.write(py2js(data))
        # f.write(py2js(data, compact=not settings.SITE.is_demo_site))
        self.serialise_js_code = False
        return 1

    def action2json(self, v):
        """Converts global list of all actions to json format."""
        assert isinstance(v, Action)
        # todo include all aux info
        # todo include grid info
        # todo refactor this into a all_actions object and have the bound actions ref it to reduse json size
        result = dict(an=v.action_name,
                      label=v.get_label(),  # todo fix this, this is a readable action, not ID for the action
                      window_action=v.is_window_action(),
                      http_method=v.http_method,
                      )

        if isinstance(v, WrappedAction):
            result['an'] = v.bound_action.action.action_name
            result['actor'] = str(v.bound_action.actor)

        if v.preprocessor: result["preprocessor"] = v.preprocessor
        # if v.combo_group: result["combo_group"] = v.combo_group
        if v.select_rows: result['select_rows'] = v.select_rows
        if v.submit_form_data: result['submit_form_data'] = True
        if v.button_text: result['button_text'] = v.button_text

        icon = self.get_action_icon(v)
        if icon: result['icon'] = icon

        return result

    def panel2json(self, p):
        assert isinstance(p, BaseLayout)
        # is a Layout instance
        # return ["foo"]
        v = p.get_layout_handle()
        return dict(main=self.elem2json(v.main),
                    window_size=v.layout.window_size)

    def elem2json(self, v):
        assert isinstance(v, LayoutElement)
        # Layout elems
        result = dict(label=v.get_label(),
                      # repr=repr(v),
                      react_name=v.__class__.__name__)  # Used for choosing correct react component
        if hasattr(v, "elements"):  # dd
            result['items'] = [self.elem2json(e) for e in v.elements if e.is_visible()]
            # result['items'] = [e for e in v.elements if e.get_view_permission(get_user_profile())]
        result.update(obj2dict(v, "fields_index fields_index_hidden editable vertical hpad is_fieldset name width preferred_width\
                                  hidden value hflex vflex"))
        # result["width"] = v.width or v.preferred_width
        # Slave tables
        if hasattr(v, "actor"):
            # reference to actor data for slave-grids
            result.update(obj2dict(v.actor, "actor_id"))  # to get siteDate layout index
            # if str(v.actor) == "system.Dashboard":
            #     print("20210617c", v.value, result)

        # if hasattr(v, "get_field_options"):
        if issubclass(v.__class__, FieldElement):
            result.update(field_options=v.get_field_options())
            result.update(help_text=v.field.help_text)

        return result

    # working, but shouldn't be used, as it clears the app history

    def reload_js(self):
        return "window.App.dashboard.reload();"

    def get_request_url(self, ar, *args, **kw):
        """Used for turn requests into urls"""
        if ar.actor.__name__ == "Main":
            return self.front_end.build_plain_url(*args, **kw)

        st = ar.get_status()
        kw.update(st['base_params'])
        add_user_language(kw, ar)
        if ar.offset is not None:
            kw.setdefault(ext_requests.URL_PARAM_START, ar.offset)
        if ar.limit is not None:
            kw.setdefault(ext_requests.URL_PARAM_LIMIT, ar.limit)
        if ar.order_by is not None:
            sc = ar.order_by[0]
            if sc.startswith('-'):
                sc = sc[1:]
                kw.setdefault(ext_requests.URL_PARAM_SORTDIR, 'DESC')
            kw.setdefault(ext_requests.URL_PARAM_SORT, sc)
        # ~ print '20120901 TODO get_request_url

        return self.front_end.build_plain_url(
            ar.actor.app_label, ar.actor.__name__, *args, **kw)

    # from extrenderer
    def action_button(self, obj, ar, ba, label=None, **kw):
        label = label or ba.get_button_label()
        if len(label) == 1:
            label = "\u00A0{}\u00A0".format(label)
            # label = ONE_CHAR_LABEL.format(label)
        if ba.action.parameters and not ba.action.no_params_window:
            st = self.get_action_status(ar, ba, obj)
            return self.window_action_button(
                ar, ba, st, label, **kw)
        if ba.action.opens_a_window:
            st = ar.get_status()
            if obj is not None:
                st.update(record_id=obj.pk)
            return self.window_action_button(ar, ba, st, label, **kw)
        return self.row_action_button(obj, ar, ba, label, **kw)

    # from ext_renderer
    def action_call_on_instance(
            self, obj, ar, ba, request_kwargs={}, **status):
        """Note that `ba.actor` may differ from `ar.actor` when defined on a
        different actor. Remember e.g. the "Must read eID card" action
        button in eid_info of newcomers.NewClients (20140422).

        :obj:  The database object
        :ar:   The action request
        :ba:  The bound action
        :request_kwargs: keyword arguments to forwarded to the child action request

        Any keyword other arguments are forwarded to :meth:`ar2js`.

        """
        if ar is None:
            sar = ba.request(**request_kwargs)
        else:

            sar = ar.spawn(ba, **request_kwargs)
        return self.ar2js(sar, obj, **status)

    def get_action_icon(self, action):
        """
        Uses an internal mapping for icon names to convert existing icons into react-usable.
        :param action:
        :return: str: a icon name for either prime-react or icon8
        """

        icon = action.react_icon_name or action.icon_name  # prioritise react_icon
        react_icon = REACT_ICON_MAPPING.get(icon, None)
        if react_icon is None:
            return None
        else:
            return "pi %s" % react_icon

    def ar2js(self, ar, obj, **status):
        """Implements :meth:`lino.core.renderer.HtmlRenderer.ar2js`.

        """
        rp = ar.requesting_panel
        ba = ar.bound_action
        params = {}
        if ba.action.is_window_action():
            # is_window_action is known in the json file, just run action as normal
            # Unsure what data is added with this, but likely want to include it.
            # print("1.19.2019", status)
            status.update(self.get_action_status(ar, ba, obj))
            params.update(status)
        params.update(self.get_action_params(ar, ba, obj))
        params.update(status)

        js_obj = {
            "rp": rp,
            "an": ba.action.action_name,
            "onMain": ar.is_on_main_actor,
            "actorId": ba.actor.actor_id,
            "status": params
        }
        if hasattr(obj, "pk"):
            js_obj["sr"] = obj.pk  # else "-99998",
            #  -99998 might be wrong for many commands... need to know what logic is used to determn it,
        elif isinstance(obj, list):
            js_obj["sr"] = obj

        return "window.App.runAction(%s)" % (
            py2js(js_obj))
        # bound_action.a)

    def py2js_converter(self, v):
        """
        Additional converting logic for serializing Python values to json.
        """
        if v is settings.SITE.LANGUAGE_CHOICES:
            return js_code('LANGUAGE_CHOICES')
        if isinstance(v, LayoutHandle):
            raise Exception("20210517 {}".format(v))
        if isinstance(v, choicelists.Choice):
            """
            This is special. We don't render the text but the value.
            """
            return v.value
        if isinstance(v, models.Model):
            return v.pk
        if isinstance(v, Exception):
            return str(v)
        if isinstance(v, Menu):
            if v.parent is None:
                return v.items
                # kw.update(region='north',height=27,items=v.items)
                # return py2js(kw)
            return dict(text=v.label, menu=dict(items=v.items))

        if isinstance(v, MenuItem):
            if v.instance is not None:
                h = self.instance_handler(None, v.instance, None)
                assert h is not None
                js = "%s" % h
                return self.handler_item(v, h, None)
            elif v.bound_action is not None:
                if v.params:
                    ar = v.bound_action.request(**v.params)
                    js = self.request_handler(ar)
                else:
                    js = self.action_call(None, v.bound_action, {})
                return self.handler_item(v, js, v.help_text)

            elif v.javascript is not None:
                js = "%s" % v.javascript
                return self.handler_item(v, js, v.help_text)
            elif v.href is not None:
                url = v.href
            # ~ elif v.request is not None:
            # ~ raise Exception("20120918 request %r still used?" % v.request)
            # ~ url = self.get_request_url(v.request)
            else:
                # a separator
                # ~ return dict(text=v.label)
                return v.label
                # ~ url = self.build_url('api',v.action.actor.app_label,v.action.actor.__name__,fmt=v.action.name)
            if v.parent.parent is None:
                # special case for href items in main menubar
                return dict(
                    xtype='button', text=v.label,
                    # ~ handler=js_code("function() { window.location='%s'; }" % url))
                    handler=js_code("function() { Lino.load_url('%s'); }" % url))
            return dict(text=v.label, href=url)

        if isinstance(v, js_code) and getattr(self, "serialise_js_code", False):
            # Convert js_code into strings so they are serialised. rather than displayed w/o quotes
            return str(v.s)

        return v

    # def goto_instance(self, ar, obj, detail_action=None, **kw):
    #     """Ask the client to display a :term:`detail window` on the given
    #     record. The client might ignore this if Lino does not know a
    #     detail window.
    #
    #     This calls :meth:`obj.get_detail_action
    #     <lino.core.model.Model.get_detail_action>`.
    #
    #     """
    #     js = self.instance_handler(ar, obj, detail_action)
    #     kw.update(eval_js=js)
    #     ar.set_response(**kw)

    def handler_item(self, mi, handler, help_text):
        """"""
        # ~ handler = "function(){%s}" % handler
        # ~ d = dict(text=prepare_label(mi),handler=js_code(handler),tooltip="Foo")
        d = dict(text=mi.label, handler=handler)
        if mi.bound_action and mi.bound_action.action.icon_name:
            d.update(iconCls='x-tbar-' + mi.bound_action.action.icon_name)
        if settings.SITE.use_quicktips and help_text:
            # d.update(tooltip=help_text)
            # d.update(tooltipType='title')
            d.update(toolTip=help_text)
        return d

    # Todo
    def request_handler(self, ar, *args, **kw):
        """ Generates js string for action button calls.
        """
        # js = super(ExtRenderer, self).request_handler(ar, *args, **kw)
        st = ar.get_status(**kw)
        return self.action_call(ar, ar.bound_action, st)

    # def instance_handler(self, ar, obj, ba, **status):
    #     return super(Renderer, self).instance_handler(ar, obj, ba, **status)

    def action_call(self, ar, bound_action, status):

        a = bound_action.action
        # fullname = ".".join(bound_action.full_name().rsplit(".", 1)[::-1])  # moves action name to first arg,
        actorId, an = bound_action.full_name().rsplit(".", 1)

        if not status:
            status = {}
        if ar and ar._status:
            status.update(ar._status)

        if ar and ar.subst_user:
            status[constants.URL_PARAM_SUBST_USER] = ar.subst_user
        if isinstance(a, ShowEmptyTable):
            status.update(record_id=-99998)
        if an == 'grid' and hasattr(status, 'record_id'):
            del status['record_id']

        rp = None if ar is None else ar.requesting_panel

        return "window.App.runAction(%s)" % py2js(dict(
            an=an,
            actorId=actorId,
            status=status,
            rp=rp))
        # return "%s()" % self.get_panel_btn_handler(bound_action)

    def js2url(self, js):
        if not js:
            return None
        # Convert to string as currently window actions are py2js => dict
        if not isinstance(js, str):
            js = str(js)
        js = escape(js, quote=False)
        return 'javascript:' + js

    def add_help_text(self, kw, help_text, title, datasource, fieldname):
        if settings.SITE.use_quicktips:
            if settings.SITE.show_internal_field_names:
                ttt = "(%s.%s) " % (datasource, fieldname)
            else:
                ttt = ''
            if help_text:
                ttt = format_lazy(u"{}{}", ttt, help_text)
            if ttt:
                # kw.update(qtip=self.field.help_text)
                # kw.update(toolTipText=self.field.help_text)
                # kw.update(tooltip=self.field.help_text)
                kw.update(quicktip="(%s,%s)" % (title,
                                                ttt))

    def lino_js_parts_chunked(self, actorId):
        """ Like lino_js_parts, but for actor_level data"""
        user_type = get_user_profile()
        filename = 'Lino_' + actorId + "_"
        file_type = self.lino_web_template.rsplit(".")[-1]  # json
        if user_type is not None:
            filename += user_type.value + '_'
        filename += translation.get_language() + '.' + file_type
        return ('cache', file_type, filename)

    def actions2json(self, actions_list):  # 20210517
        """Converts of all the boundactions of an actor to json format.
        """
        # v is a dict of an -> BoundCction instances
        result = []
        hotkeys = []

        for ba in actions_list:
            lh = ba.get_layout_handel()
            if (lh or ba.action.window_type):

                action_descriptor = {'an': ba.action.action_name}
                if lh:
                    action_descriptor.update(window_layout=lh.layout._formpanel_name)
                if ba.action.window_type:
                    tbas = []
                    combo_map = dict()

                    for a in ba.actor.get_toolbar_actions(
                        ba.action, get_user_profile()):

                        tba = dict(an=a.action.action_name)
                        help_text = a.action.help_text
                        if help_text: tba['help_text'] = help_text
                        js_handler = a.action.js_handler
                        if js_handler:
                            if callable(js_handler):
                                tba['js_handler'] = js_handler(a.actor)
                            else:
                                tba['js_handler'] = js_handler

                        if a.action.combo_group is not None:
                            combo_group = a.action.combo_group

                            if combo_group in combo_map:
                                combo_map[combo_group].append(tba)
                            else:
                                combo = dict(combo=combo_group)
                                combo_map[combo_group] = [tba]
                                tbas.append(combo)
                        else:  # is normal
                            tbas.append(tba)

                        if a.action.hotkey:
                            hotkey = vars(a.action.hotkey)
                            if not hasattr(hotkey, 'ba'):
                                hotkey['ba'] = a.action.action_name
                            if hotkey not in hotkeys:
                                hotkeys.append(hotkey)

                    if combo_map:
                        for i, tba in enumerate(tbas):
                            if tba.get('combo', False):
                                tbas[i]['menu'] = combo_map[tba['combo']]

                    action_descriptor["toolbarActions"] = tbas

                result.append(action_descriptor)

            if ba.action.hotkey:
                hotkey = vars(ba.action.hotkey)
                if not hasattr(hotkey, 'ba'):
                    hotkey['ba'] = ba.action.action_name
                if hotkey not in hotkeys:
                    hotkeys.append(hotkey)

        return result, hotkeys

    def actor2json(self, v):
        assert isclass(v) and issubclass(v, Actor)
        al , hk = self.actions2json(v._actions_list)
        result = dict(id=v.actor_id,
                      actions_list=al,
                      label=v.get_actor_label(),
                      slave=bool(v.master),
                      editable=not v.hide_editing(get_user_profile())
                      # [py2js(b) for b in v.actions.items()]
                      )
        if len(hk):
            result.update(hotkeys=hk)

        ah = v.get_handle()
        if ah.store is None:
            settings.SITE.logger.warning("%s has no store", v)
        else:
            # grids
            if hasattr(ah, "get_columns"):
                columns = []
                index_mod = 0
                col_elems = ah.get_columns()
                for col in col_elems:
                    d = self.elem2json(col)
                    d.update(fields_index = find(ah.store.list_fields, col.field.name,
                                          key=lambda f: f.name) + index_mod)
                    if isinstance(col, ComboFieldElement) and not isinstance(col, SimpleRemoteComboFieldElement):
                        # Skip the data value for multi value columns, such as choices and FK fields.
                        # use c.fields_index -1 for data value
                        d.update(fields_index_hidden = d['fields_index'] + 1)
                        index_mod += 1
                    columns.append(d)
                result['col'] = columns
                # (dict(main=self.elem2json(col_elems.main),
                #         col=columns,
                #        window_size=col_layout.layout.window_size))

            result.update(obj2dict(ah.store, "pk_index"))  # Data index which is the PK
        result.update(obj2dict(v, "preview_limit "  # number of rows to render # if 0 no paginator.
                                  "use_detail_param_panel "  # show PV panel in detail
                                  "use_detail_params_value "  # in grid, use parrent PV values
                                  "hide_navigator "
                                  "use_detail_params_value "
                                  "react_responsive "
                                  "display_mode "
                                  "max_render_depth "
                                  "simple_slavegrid_header "
                                  "paginator_template "
                                  "hide_top_toolbar "
                                  "hide_if_empty "
                               ))

        if hasattr(v.model, "file"):
            result.update(contain_media=True)

        if v.detail_action is not None:
            wl = v.detail_action.get_window_layout()
            if wl is not None:
                result.update(window_layout=wl._formpanel_name)

        if v.active_fields:
            result.update(active_fields=list(v.active_fields))

        card_layout = getattr(v, "card_layout", None)
        if card_layout is not None:
            result.update(card_layout=card_layout._formpanel_name)

        item_layout = getattr(v, "item_layout", None)
        if item_layout is not None:
            # print("20210629", v, "item_layout is", item_layout)
            result.update(item_layout=item_layout._formpanel_name)
        # mt + slave-tables

        chooser_dict = getattr(v.model, "_choosers_dict", {})
        if chooser_dict:
            result.update(chooser_dict={fn: [cf.name for cf in c.context_fields]
                                        for fn, c in chooser_dict.items()})

        if settings.SITE.is_installed('contenttypes') and getattr(v, 'model', None) is not None and hasattr(v.model,
                                                                                                            "_meta"):
            # Perhaps I should have the model also be py2js'd?
            result.update(content_type=ContentType.objects.get_for_model(v.model).pk)
        for k in ("detail_action", "insert_action", "default_action"):
            ba = getattr(v, k, None)
            if ba is not None:
                result.update({k: ba.action.action_name})

        if v.params_layout is not None:
            # Param field array and layout struct
            result.update(
                params_layout=v.params_layout._formpanel_name,
                params_fields=[f.name for f in v.params_layout.params_store.param_fields],
            )
            if hasattr(v, "params_panel_pos"):
                result.update(params_panel_pos=v.params_panel_pos)
        return result

    def build_js_cache(self, force):
        self.serialise_js_code = True

        for actor in self.actors_list:
            fn = path.join(*self.lino_js_parts_chunked(actor.actor_id))

            def write(f):
                f.write(
                    py2js(self.actor2json(actor))
                )

            settings.SITE.kernel.make_cache_file(fn, write, force)

        self.serialise_js_code = False

        return super(Renderer, self).build_js_cache(force)
