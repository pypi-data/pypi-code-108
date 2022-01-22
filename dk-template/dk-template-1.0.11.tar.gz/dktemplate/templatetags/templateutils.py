# -*- coding: utf-8 -*-
import traceback

import re
from dk.collections import pset
from django import template


NO_VALUE = '4242424242'


def split_lines(text):
    """Split text into lines.
       Removes comments, blank lines, and strips/trims whitespace.
    """
    lines = []
    for line in text.splitlines():
        if '#' in line:
            line = line[:line.index('#')]
        line = line.strip()
        if line:
            lines.append(line)
    return lines


def remove_comments(text):
    "Remove comments, blank lines, and strip/trim whitespace."
    return u'\n'.join(split_lines(text))


class Env(pset):
    """Utility class for easier look-ups in the context.

       Instead of writing::

           def render(self, ctx):
               ctx.push()
               foo = template.Variable('foo').resolve(ctx)
               ctx['bar'] = foo.x + 1
               res = self.nodes.render(ctx)
               ctx.pop()
               return res

       you can now write::

           def render(self, ctx):
               with Env(ctx) as env:
                   env.bar = env.foo.x + 1
                   return self.nodes.render(ctx)

       use ``Env(ctx, scope=False)`` if you do not want the context protection
       around your code block (ie. no ``ctx.push()`` and ``ctx.pop()``.
    """

    def __init__(self, ctx, scope=True):
        self._ctx = ctx
        self._scope = scope
        super(Env, self).__init__()

    def contains(self, key):
        "Test if variable ``key`` is defined in the context."
        try:
            template.Variable(key).resolve(self._ctx)
            return True
        except template.VariableDoesNotExist:
            return False

    def __setattr__(self, key, val):
        if key.startswith('_'):
            object.__setattr__(self, key, val)
        else:
            self._ctx[key] = val

    def __getattr__(self, key):
        if key not in self:
            self[key] = template.Variable(key).resolve(self._ctx)
        return dict.get(self, key)

    def __enter__(self):
        if self._scope:
            self._ctx.push()
        return self

    def __exit__(self, tp, value, traceback):
        if self._scope:
            self._ctx.pop()


class DkNode(template.Node):
    """Pull __init__ method up into a common superclass.

       Works in conjunction with ``deftag`` (below), so you can do::

          class FooNode(DkNode):
              def render(self, ctx):
                  return self.nodes.render(ctx)

          foo = deftag('foo')

       which is considerably much less boilerplate code.
    """

    def __init__(self, dkargs, nodes):
        super(DkNode, self).__init__()
        self.args = dkargs
        self.nodes = nodes


def deftag(tagname, cls, has_endtag=True):
    """Boilerplate code for creating a tag *function* who's only purpose is
       calling the corresponding Node class' init.

       Usage::

        from dkdjango.templatetags.templateutils import deftag as _deftag

        def deftag(*args, **kwargs):
           return register.tag(*_deftag(*args, **kwargs))

    """

    def tagfn(parser, token):
        "Default/generic tag function."
        try:
            args = DKArguments(token)
            # if settings.DEBUG:
            #    print tagname, 'args:', args
            if has_endtag:
                nodes = parser.parse(['end' + tagname])
                parser.delete_first_token()
            else:
                nodes = None
            return cls(args, nodes)
        except:  # noqa
            traceback.print_exc()
            raise template.TemplateSyntaxError(traceback.format_exc())

    if cls.__doc__:
        tagfn.__doc__ = cls.__doc__

    return tagname, tagfn


dkarg_re = re.compile(r'''
  ((?P<left>\|)?
   (?P<argname>[-_\w]+(\.\w+)*)
   (?P<right>\|)?
   =?
   (
    ("(?P<dqval>[^"]*)")
   |('(?P<sqval>[^']*)')
   |(?P<boolval>(True)|(False))
   |(?P<floatval>\d+\.\d+)
   |(?P<dotval>\w+(\.\w+)+)
   |(?P<intval>\d+)
   |(?P<lambda>\((?P<lambda_args>\w+)\){(?P<lambda_body>.*?)})
   |(?P<val>[^ ]+)
   )?
  )
 |(
    ("(?P<dqvalue>[^"]*)")
   |('(?P<sqvalue>[^']*)')
  )
   ''',  # " keep emacs highlighting happy...

                      re.MULTILINE | re.VERBOSE)


class ArgValues(object):
    """Descriptor to access a templates argument values given the current
       context.
    """

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError("ArgValues is an instance attribute.")

        class proxy(object):
            """Proxy object for the arguments to the template (ie. ``obj``).

               Usage (template)::

                   {% foo argname=tmplvar %}

               ::
                   def render(self, ctx):
                       self.args.ctx = ctx
                       tmplvar = self.args.lookup.argname

               Since all template arguments must be on one line, the linear
               search shouldn't be a problem (in fact it should be faster
               than a dict lookup in most cases).

            """

            def __getitem__(self, attr, default=None):
                return getattr(self, attr, default)

            def get(self, attr, default=None):
                try:
                    return getattr(self, attr, default)
                except template.VariableDoesNotExist:
                    return default

            def __getattr__(pself, attr):
                val = None
                for arg in obj.args:
                    if arg.name == attr:
                        if arg.kind == 'ctxvar':
                            if obj.ctx is None:
                                msg = 'templateutils.Arguments.ctx not set!'
                                raise RuntimeError(msg)

                                # Variable resolution should be done by calling
                                # template.Variable(variable-name).resolve(context)
                                # however, that method will try to call __call__
                                # on the object, and e.g. data sources have
                                # a __call__ method that cannot take zero
                                # arguments (thus raising a TypeError).
                                # XXX: needs better fix?
                            #                            possible_val = [x for x in [d.get(arg.value) for d in obj.ctx] if x]
                            #                            if possible_val:
                            #                                val = possible_val[0]
                            #                            else:
                            #                                val = ''
                            val = template.Variable(arg.value).resolve(obj.ctx)

                        else:
                            val = arg.value
                        return val
                raise AttributeError(attr)

        return proxy()

    def __set__(self, obj, value):
        "Make this a data descriptor."
        raise AttributeError


class Arguments(object):
    """Usage::

           @register.tag
           def pivot(parser, token):
               try:
                   args = templateutils.Arguments(token)
                   print args
                   return PivotNode(args)
               except:
                   traceback.print_exc(file=sys.stdout)

           class PivotNode(template.Node):
               def __init__(self, args):
                   self.name = args[0].value  # positional value parameters
                   self.args = {     # provide defaults for all possible parameters
                       'foo':  bar,
                       ...
                       }
                   for arg in args[1:]:   # we consumed [0] above
                       self.args[arg.name] = arg.value

       Syntax::

           {% tagname args %} where args can be any of...

             "value"
             'value'
             arg=param
             |arg=param        left justify
             arg|=param        right justify
             |arg|=param       center

           param can be any of
             "value"           string
             'value'
             True              booleans
             False
             3.14159           float
             rec.field         dotted notation
             42                integers
             (arg){body}       lambda expression
             <any-but-space>   any series of characters except space

    """
    lookup = ArgValues()  #: descriptor lookup

    def __init__(self, token=None, raw_contents=None):
        self.ctx = None
        if token is not None:
            self.raw_contents = token.contents
        else:
            self.raw_contents = raw_contents
        #: the name of the tag itself
        self.tagname = self.raw_contents.split(' ', 1)[0]
        #: a list of pset(name, align, kind, value)
        self.args = []
        #: a dict from name to value
        self.argnames = {}

        self._parse(self.raw_contents[len(self.tagname) + 1:].strip())

        #: a list of all args that are specified with a no-prefix (which sets
        #: the corresponding unprefixed arg to False.
        self.nonames = [argname for argname in self.argnames
                        if argname
                        and argname.startswith('no')
                        and argname[2:] not in self.argnames]
        for name in self.nonames:
            self.add_argument(name[2:], align='left', kind='bool', value=False)

    def __getitem__(self, key):
        return self.args[key]

    def __contains__(self, argname):
        return argname in self.argnames

    def add_argument(self, name, align, kind, value):
        """Add an argument to self.
        """
        arg = pset(name=name, align=align, kind=kind, value=value)
        self.args.append(arg)
        self.argnames[name] = value
        return arg

    def remove_argument(self, name):
        """Remove an argument from self.
        """
        if name not in self.argnames:
            return
        del self.argnames[name]
        for i, arg in enumerate(self.args):
            if arg.name == name:
                break
        else:
            return  # pragma: nocover
        del self.args[i]

    def update_context(self, skip=None):
        if skip is None:
            skip = set()
        for arg in self.args:
            if arg.name not in skip:
                self.ctx[arg.name] = self.lookup.get(arg.name)

    def _find(self, attr):
        """Return the attribute named attr.
        """
        if attr.startswith('_'):
            return None
        for arg in self.args:
            if arg.name == attr:
                return arg
        return None

    def get_value(self, attr, default=None):
        a = self._find(attr)
        if a is None:
            return default
        if a.value is NO_VALUE:
            return default
        return a.value

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            for arg in self.args:
                if arg.name == attr:
                    return arg

    def pop(self, attrname):
        """Return and remove argument with ``key``.
        """
        res = self._find(attrname)
        if res is None:
            return None
        self.remove_argument(attrname)
        return res

    def __len__(self):
        return len(self.args)

    def __repr__(self):
        import pprint
        return pprint.pformat(self.__dict__)

    # below here is parser routines.
    def _parse(self, txt):
        """Parse the contents of the tag.
        """
        i = 0
        while txt:
            txt = self._parse_next_argument(txt)
            i += 1
            if i > 100:
                raise ValueError('too many arguments')

    def _parse_next_argument(self, txt):
        """Parse the next argument from txt, adding it to self.args and
           self.argnames, and returning the remaining txt.
        """
        m = dkarg_re.match(txt)
        g = m.groupdict()
        tp, val = self._value(g)
        name = g['argname']
        align = self._parse_align(g)
        self.add_argument(name, align, tp, val)
        return txt[m.span()[1]:].strip()

    def _parse_align(self, grpdict):
        align = 'left'
        if grpdict['right']:
            align = 'right'
        if align == 'right' and grpdict['left']:
            align = 'center'
        return align

    def _value(self, grpdict):
        g = grpdict
        if g['val']:
            return 'ctxvar', g['val']
        elif g['sqval']:
            return 'string', g['sqval']
        elif g['dqval']:
            return 'string', g['dqval']
        elif g['boolval']:
            return 'bool', eval(g['boolval'])
        elif g['floatval']:
            return 'float', eval(g['floatval'])
        elif g['dotval']:
            return 'dotval', [str(v) for v in g['dotval'].split('.')]
        elif g['intval']:
            return 'int', eval(g['intval'])
        elif g['lambda']:
            return 'lambda', eval("lambda %s:%s" % (g['lambda_args'],
                                                    g['lambda_body']))
        elif g['dqvalue']:
            return 'string', g['dqvalue']
        elif g['sqvalue']:
            return 'string', g['sqvalue']

        else:
            return 'unknown', NO_VALUE


class DKArguments(Arguments):
    "Backwards compatibility class, don't use for new code."

    def _value(self, grpdict):
        g = grpdict
        if g['val']:
            return 'string', g['val']
        else:
            return super(DKArguments, self)._value(grpdict)
