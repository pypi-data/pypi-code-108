# Copyright 2010-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from importlib import import_module


simplify_parts = set(
    ['models', 'desktop', 'ui', 'choicelists', 'actions', 'mixins'])

def simplify_name(name):
    """
    Simplify the given full Python name.

    Removes any part 'models', 'desktop', 'ui', 'choicelists',
    'mixins' or 'actions' from the name.

    This is used when we want to ignore where exactly a model or table
    or action is being defined within its plugin.
    """
    if name.startswith("lino.mixins."):
        return name
    parts = name.split('.')
    for e in simplify_parts:
        if e in parts:
            parts.remove(e)
    return '.'.join(parts)


class HelpTextsLoader:

    _help_texts = dict()

    def __init__(self, site):
        self.load_help_texts(site)

    def load_help_texts(self, site):
        """Collect :xfile:`help_texts.py` modules"""
        for p in site.installed_plugins:
            mn = p.app_name + '.help_texts'
            try:
                m = import_module(mn)
                # print("20160725 Loading help texts from", mn)
                self._help_texts.update(m.help_texts)
            except ImportError:
                pass

    def get_help_text_for_class(self, m, attrname=None):
        k = m.__module__ + '.' + m.__name__
        k = simplify_name(k)
        # debug = k.startswith('users')
        if attrname:
            k += '.' + attrname
        txt = self._help_texts.get(k, None)
        return (k, txt)

    def install_help_text(self, fld, cls=None, attrname=None):
        """
        Set the `help_text` attribute of the given element `fld` from
        collected :xfile:`help_texts.py`.
        """
        if cls is None:
            cls = fld
        debug = False
        # debug = attrname == 'municipality'
        # debug = attrname == 'municipality' and cls.__name__ == "Client"
        # try:
        #     str(fld)
        # except TypeError as e:
        #     raise Exception("{} : {}".format(repr(fld), e))
        # debug = cls.__name__ == "User"
        # debug = True
        if not hasattr(fld, 'help_text'):
            # e.g. models or plugins don't have a help_text attribute
            if debug:
                print("20170824 {!r} has no help_text".format(fld))
            return
        for m in cls.mro():
            # useless = ['lino.core', 'lino.mixins']
            # if m.__module__.startswith(useless):
            #     continue
            # if m in self.unhelpful_classes:
            #     continue
            k, txt = self.get_help_text_for_class(m, attrname)
            # if attrname == "update_missing_rates":
            #     print("20181004 {} {} {}".format(cls, k, txt))
            if txt is None:
                if debug:
                    print("20170824 {}.{} : no help_text using {!r}".format(
                        cls, attrname, k))
                if fld.help_text:
                    # hard-coded help text gets overridden only if docs
                    # provide a more specific help text.
                    return

            else:
                if debug:
                    # from lino.api import dd
                    # dd.logger.info("20200818 site.py %s", fld.__hash__())
                    print("20170824 {}.{}.help_text {!r} found using {} --> {}".format(
                        cls, attrname, txt, k, fld))
                fld.help_text = txt
                fld._lino_help_ref = k  # for makedocs
                return
        if debug:
            print("20170824 {}.{} : no help_text".format(
                cls, attrname))
