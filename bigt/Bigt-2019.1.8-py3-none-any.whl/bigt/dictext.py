import re
import sys
import inspect
from copy import deepcopy
from collections.abc import Iterable

# sphinx-build -b html source build
# sphinx-apidoc -f -o source ../bigt
# docstr-coverage bigt -m -f
# pytest --cov=bigt tests/ --cov-report annotate


def _xstr(s):
    """Get empty str in case of None and str in other case.

    Arguments:
        s ``object`` -- object to cast it to str

    Returns:
        ``str`` -- str represenration
    """
    return '' if s is None else str(s)


def _str_to_bool(s):
    """Convert str to bool

    Arguments:
        s ``str`` -- str to convert

    Returns:
        ``bool`` -- bool value

    How it works:
        ::

            >>> _str_to_bool("false")
            False
            >>> _str_to_bool(1)
            True
    """
    return str(s).lower() in ("yes", "true", "t", "1")


class DictExt(dict):
    """Extention of the inbuild dict type.
    Main reason is add simple actions like +, -
    to simplify working with dictionaries.
    """

    def __getattribute__(self, name):
        if name in self:
            return DictExt(self[name]) \
                if isinstance(self[name], dict) \
                else self[name]
        else:
            return object.__getattribute__(self, name)

    def __sub__(self, other):
        _, x, y = self.issubset(other)
        return DictExt(x) + DictExt(y)

    def __add__(self, other):
        return DictExt(self.merge(other))

    def __ge__(self, other):
        return comparators[dict].diff(other, self)[0]

    def __le__(self, other):
        return comparators[dict].diff(self, other)[0]

    def __eq__(self, other):
        return str(DictExt(self).sort()) == str(DictExt(other).sort())

    def __ne__(self, other):
        return str(self.sort()) != str(DictExt(other).sort())

    def issubset(self, other, regex_mask=False, skip=[], weights={}):
        """Return is ``this`` is a subset of ``other`` dict.

        Arguments:
            other ``DictExt`` -- dict in which subset will be checked.

        Keyword Arguments:
            regex_mask ``bool`` -- Turn on the processing of regular expression
            as values. (default: ``False``)

            skip ``list`` -- Dot separated path to elements that should be
            skipped from the result. (default: ``[]``)

                Example::

                    ['path.sub.a']
        Returns:
            ``tuple``:
                * Bool value is 'this' is a subset of 'other' dict.
                * Not present elements dict.
                * Changed elements dict.

        How to use:
            ::

                a = {"a": {"a": "str", "b": 123}}
                b = {"a": {"a": "str", "b": 1234}}
                result, not_present, changed = DictExt(b).issubset(a)
                assert not result
                assert changed == {"a": {"b": {"old": 1234, "new": 123} } }
                assert not not_present
        """
        return comparators[dict].diff(
            self, other, regex_mask, skip, weights=weights)

    def sort(self):
        """Sort dict.

        Returns:
            ``DictExt`` -- Sorted DictExt object.

        How it works:
            ::

                >>> DictExt({
                        "aa": 3,
                        "a": [{"b": {"bv": 1, "bc": 2}, "a": 1}, [3,1,8,5]]
                    }).sort()
                {
                    'a': [[1, 3, 5, 8], {'a': 1, 'b': {'bc': 2, 'bv': 1}}],
                    'aa': 3
                }
        """

        def df(x):
            return DictExt({"_": x}).sort()["_"]

        def filterType(t, v):
            return filter(lambda x: isinstance(x, t), v)
        d = DictExt(sorted(self.items()))
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = DictExt(v).sort()
            elif isinstance(v, list):
                d[k] = sorted(filter(lambda x: not isinstance(x, Iterable), v))
                d[k].extend(
                    sorted([df(x) for x in filterType(list, v)],
                           key=lambda x: len(x)))
                d[k].extend(
                    sorted([df(x) for x in filterType(dict, v)],
                           key=lambda x: len(x)))
        return d

    def merge(self, other, path=[]):
        """Merge dict to other

        Arguments:
            other ``DictExt`` -- Dict which should be marged to current.

        Keyword Arguments:
            path ``list`` -- Path to current dict element. (default: ``[]``)

            Example::

                ['path.sub.a']

        Raises:
            Exception: If element type is not supported

        Returns:
            ``DictExt`` -- Merged dict.

        How it works:
            ::

                >>> DictExt({"a": 3, "b": [{"b": 123}]})
                    .merge(DictExt({"a": 1, "c": False, "b": [{"a": 12.64}]}))
                {'a': 1, 'b': [{'b': 123, 'a': 12.64}], 'c': False}
        """
        this = deepcopy(self)
        for key, value in other.items():
            if key in this:
                if type(this[key]) in comparators:
                    this[key] = comparators[type(this[key])].marge(
                        this[key],
                        value,
                        path + [key])
                else:
                    raise Exception('Conflict at "%s"' % '.'
                                    .join(path + [str(key)]))
            else:
                this[key] = value
        return DictExt(this)


class _default():
    "Default class to implement idea of the ``diff`` and ``merge`` methods."

    def __init__(self, this_name='old', other_name='new'):
        """Initialize Default comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case
                of diffence of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        self.type = object
        self.this_name = this_name
        self.other_name = other_name

    def diff(self, this, other, compare, weights={}):
        """Default comparison method.

        Arguments:
            this ``object`` -- element which should be compared
            other ``object`` -- element to compare with
            compare ``func`` -- comparison function

        Returns:
            ``tuple``:
                * Bool value is 'this' is different from 'other'.
                * None.
                * None.
        """
        result = compare(this, other)
        return result, None, None \
            if result else {self.this_name: this, self.other_name: other}

    def marge(self, this, other, *args):
        """Default merge method for simple types.

        Arguments:
            this ``object`` -- element which should be marged
            other ``object`` -- element that should be marged to ``this``

        Returns:
            ``object`` -- merged element
        """
        return other


class _simple(_default):
    "Class to compare simple types"

    def diff(self, this, other, *args):
        """Simple types comparison method.

        Arguments:
            this ``object`` -- element which should be compared
            other ``object`` -- element to compare with
            compare ``func`` -- comparison function

        Returns:
            ``tuple``:
                * Bool value is 'this' is different from 'other'.
                * None.
                * None.
        """
        return super().diff(this, other, lambda x, y: _xstr(x) == _xstr(y))


class _int(_simple):
    "Class to compare int values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize int comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case
                of diffence of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = int
        self.default = 0


class _float(_simple):
    "Class to compare int values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize float comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case
                of diffence of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence of
                elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = float
        self.default = 0.0


class _bool(_default):
    "Class to compare bool values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize float comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case of diffence
                of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = bool

    def diff(self, this, other, *args):
        """Boolean comparison method.

        Arguments:
            this ``bool`` -- element which should be compared
            other ``bool`` -- element with which comparison should be performed

        Returns:
            ``tuple``:
                * Bool value is 'this' is different from 'other'.
                * None.
                * None.
        """
        return super().diff(
            this, other, lambda x, y: _str_to_bool(x) == _str_to_bool(y))

    def marge(self, this, other, *args):
        """Bool merge method.

        Arguments:
            this ``bool`` -- element which should be marged
            other ``bool`` -- element that should be marged to ``this``

        Returns:
            ``bool`` -- merged element
        """
        return _str_to_bool(other)


class _str(_default):
    "Class to compare str values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize float comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case of diffence
                of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = str
        self.default = ""

    def diff(self, this, other, regex=False, *args):
        """String comparison method.

        Arguments:
            this ``str`` -- element which should be marged
            other ``str`` -- element that should be marged to ``this``

        Keyword Arguments:
            regex ``bool`` -- Turn on the processing of regular expression
                as values. (default: ``False``)

        Returns:
            ``tuple``:
                * Bool value is 'this' is different from 'other'.
                * None.
                * None.
        """
        return super().diff(this, other,
                            lambda x, y: bool(re.findall(x, _xstr(y)))
                            if regex else x == _xstr(y))


class _dict(_default):
    "Class to compare dict values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize dict comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case of diffence
                of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = dict

    def diff(self, this, other, regex=False, skip=[], path='', weights={}):
        """Dictionary comparison method.

        Arguments:
            this ``dict`` -- element which should be marged
            other ``dict`` -- element that should be marged to ``this``

        Keyword Arguments:
            regex ``bool`` -- Turn on the processing of regular expression
                as values. (default: ``False``)
            skip ``list`` -- Dot separated path to elements that should be
                skipped from the result. (default: ``[]``)
            path ``str`` -- Path to current dict element. (default: ``''``)

        Returns:
            Returns:
            ``tuple``:
                * Bool value is 'this' is different from 'other'.
                * Not present elements dict.
                * Changed elements dict.
        """
        result, changed, not_present = True, {}, {}
        for key, value in this.items():
            current_path = f"{path}.{key}" if path else key
            _weights = weights[key] if key in weights else {}
            if current_path in skip:
                continue
            value = self._get_default_if_none(other, key, value)
            r, n, c = comparators[type(value)]. \
                diff(value, other[key], regex, skip, current_path, _weights) \
                if self._can_compare(other, key, value) \
                else (False, value, {})
            result = result & r
            self._update_by_not_none(changed, key, c)
            self._update_by_not_none(not_present, key, n)
        return result, not_present, changed

    def marge(self, this, other, path):
        """Dictionary merge method.

        Arguments:
            this ``dict`` -- element which should be marged
            other ``dict`` -- element that should be marged to ``this``
            path ``list`` -- Path to current dict element. (default: ``[]``)

        Returns:
            ``DictExt`` -- Merged dict.
        """
        return DictExt(this).merge(other, path)

    def _update_by_not_none(self, collection, key, value):
        """Update dict with key and value if value not None.

        Arguments:
            collection ``dict`` -- dictionary that should be updated
            key ``str`` -- key to add
            value ``object`` -- element to add
        """
        if value:
            collection.update({key: value})

    def _get_default_if_none(self, other, key, value):
        """Get default attribute if it is None

        Arguments:
            other ``object`` -- object to check
            key ``str`` -- key to get
            value ``object`` -- value to check

        Returns:
            ``object`` -- value if it was ``None``,
                default value for current type will be returned
        """
        if not value and isinstance(other, dict) and key in other:
            key = other[key] if other[key] is not None else ''
            return comparators[type(key)].__dict__.get("default", value)
        else:
            return value

    def _can_compare(self, other, key, value):
        """Check is it possible to compare elements.

        Arguments:
            other ``object`` -- elements to check
            key ``str`` -- key to check
            value ``object`` -- value to check

        Returns:
            ``bool`` -- is it possible to compare elements
        """
        return isinstance(other, dict) \
            and other and value is not None and key in other


class _dictext(_dict):
    "Class to compare DictExt values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize DictExt comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case of diffence
                of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = DictExt


class _list(_default):
    "Class to compare list values"

    def __init__(self, this_name='old', other_name='new'):
        """Initialize list comparison class.

        Keyword Arguments:
            this_name ``str`` -- used for current name key in case of diffence
                of elements (default: ``'old'``)
            other_name ``str`` -- used for name key in case of diffence
                of elements for item with which comparison performs
                (default: ``'new'``)
        """
        super().__init__(this_name, other_name)
        self.type = list

    def diff(
            self, this_list, other_list,
            regex=False, skip=[], path='', weights={}):
        """List comparison method.

        Arguments:
            this_list ``list`` -- element which should be marged
            other_list ``list`` -- element that should be marged

        Keyword Arguments:
            regex ``bool`` -- Turn on the processing of regular expression
                as values. (default: ``False``)
            skip ``list`` -- Dot separated path to elements that should be
                skipped from the result. (default: ``[]``)
            path ``str`` -- Path to current dict element. (default: ``''``)
            weights ``dict`` -- weights for keys comparison. (default: ``{}``)

        Returns:
            Returns:
            ``tuple``:
                * Bool value is 'this' is different from 'other'.
                * Not present elements dict.
                * Changed elements dict.
        """

        def filter_skip(items):
            return filter(lambda x: f"{path}.{x[0]}"
                          if path else x[0] not in skip, items)

        result, not_present, changed = True, [], []
        for this in this_list:
            min_not_present, min_changed = None, None
            filtered = dict(filter_skip(this.items())) \
                if isinstance(this, dict) else this
            for other in other_list:
                r, n, c = comparators[type(this)] \
                    .diff(filtered, other, regex, skip, path, weights)
                if min_not_present is None:
                    min_not_present = n
                if min_changed is None:
                    min_changed = c
                if self._coefficient(min_not_present, min_changed, weights) \
                        > self._coefficient(n, c, weights):
                    min_not_present, min_changed = n, c
                if r:
                    break
            else:
                result = False
                skipped = len(this) - len(filtered) \
                    if isinstance(this, Iterable) else 0
                if min_changed and min_not_present and \
                    len(this) - skipped == \
                        len(min_not_present) + len(min_changed):
                    min_changed, min_not_present = None, this
                self._append_by_not_none(changed, min_changed)
                self._append_by_not_none(not_present, min_not_present)
        return result, not_present, changed

    def marge(self, this, other, path):
        """Dictionary merge method.

        Arguments:
            this ``list`` -- element which should be marged
            other ``list`` -- element that should be marged to ``this``
            path ``list`` -- Path to current dict element. (default: ``[]``)

        Returns:
            ``list`` -- Merged list.
        """
        for index, i in enumerate(other):
            if index < len(this):
                temp = comparators[type(this[index])]\
                    .marge(this[index], i, path + [str(index)])
                if i != temp:
                    this[index] = temp
                elif temp not in this:
                    this.append(temp)
            else:
                this.append(i)
        return this

    def _append_by_not_none(self, collection, value):
        """Add value to ``collection`` if value not None.

        Arguments:
            collection ``list`` -- list that should be updated
            value ``object`` -- element to add
        """
        if value:
            collection.append(value)

    def _coefficient(self, not_present, changed, weights={}):
        """Calculate coefficient for ``not_present`` and ``changed`` collection
        to compare this elements.

        Arguments:
            not_present ``dict`` -- Not present elements dict
            changed ``dict`` -- Changed elements dict

        Returns:
            ``float`` -- coefficient to compare ``comparators`` results.
        """
        def if_present(k):
            if type(weights) != dict or k not in weights:
                return 1
            if type(weights[k]) == int:
                return weights[k]
            else:
                return 1

        def calculate(a, func):
            n = 0
            for k, v in (a or {}).items():
                if type(v) == dict and k in weights:
                    n += func(k, v)
                n += 1 * if_present(k)
            return n

        n, c = 0, 0
        n = calculate(
            not_present,
            lambda k, v: self._coefficient(v, None, weights[k]))
        c = calculate(
            changed,
            lambda k, v: self._coefficient(None, v, weights[k]))
        return (n * 1.000001) + c


clsmembers = [x[1] for x in inspect.getmembers(sys.modules[__name__],
                                               inspect.isclass)]
comparators = dict([(x().type, x())
                    for x in clsmembers if issubclass(x, _default)])
