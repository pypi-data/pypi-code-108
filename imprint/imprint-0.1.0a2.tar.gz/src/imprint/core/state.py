# -*- coding: utf-8 -*-

# imprint: a program for creating documents from data and content templates
#
# Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
# Version: 13 Apr 2019: Initial Coding


"""
The :py:mod:`imprint.core.state` module supplies the state objects that
enable communication within the :ref:`introduction-layers-engine`
between the engine itself and the tags. The state is therefore crucial
to the :ref:`tag-api` without being completely a part of it.
"""

from collections import deque
from contextlib import contextmanager
from enum import Enum, unique
from itertools import repeat
from io import StringIO
import logging
from operator import index
from os.path import abspath, splitext

from haggis.files.docx import is_paragraph_empty, delete_paragraph, list_number

from . import defaults
from .utilities import aggressive_strip


__all__ = ['ReferenceMap', 'ReferenceState', 'ListType', 'EngineState']


class ReferenceMap:
    """
    A multi-level mapping that stores references in the values.

    Values are accessed through a three-level key
    ``(role, attribute, key)``: For a given
    :ref:`xml-spec-attributes-role`, the type of key is determined by
    the ``attribute`` that names the target. Most tags only support
    ``attribute='id'``, but :ref:`xml-spec-tags-segment-ref` also
    supports ``attribute='title'``. ``key`` is the actual value of the
    attribute that is used to identify the reference.

    Reference values can be any object whose :py:meth:`~object.__str__`
    method returns the correct replacement text for the reference.
    """
    # TODO: Add this class to haggis (as a generic multi-level mapping).
    def __new__(cls, *args, **kwargs):
        """
        Ensure that the map is unlocked when it is first created.

        This way calling :py:meth:`~object.__init__` is **not** a trick
        for unlocking the map.
        """
        self = super().__new__(cls, *args, **kwargs)
        self.__dict__['_locked'] = False
        self.__dict__['_mapping'] = {}
        return self

    @property
    def _locked(self):
        """
        Checks if this mapping is locked.

        This property can be set to :py:obj:`True` at any time. After
        it is set to :py:obj:`True`, it can never be set back to
        :py:obj:`False`, and none of the setter operations will work.
        """
        return self.__dict__['_locked']

    @_locked.setter
    def _locked(self, value):
        """
        Setter for :py:attr:`_locked`.
        """
        if value:
            self.__dict__['_locked'] = True
        elif self._locked:
            cls = type(self).__name__
            raise ValueError(f'Unlocking a locked {cls} is forbidden!')

    @property
    def _mapping(self):
        """
        Hidden attribute.
        """
        cls = type(self).__name__
        raise AttributeError(f'{cls} object has no attribute "_mapping"')

    def __getitem__(self, key):
        """
        Retreive the value for the specified three-level key.
        """
        role, attr, ref = self._check_key(key)
        role_map = self.__dict__['_mapping']
        try:
            attr_map = role_map[role]
        except KeyError:
            raise KeyError(f'No such role {role!r}')
        try:
            ref_map = attr_map[attr]
        except KeyError:
            raise KeyError(f'No such attribute {attr!r} for {role!r}')
        try:
            return ref_map[ref]
        except KeyError:
            raise KeyError(f'{role!r} has no key {ref!r} '
                           f'under attribute {attr!r}')

    def __setitem__(self, key, value):
        """
        If this mapping is not locked, set the attribute for the
        specified three-level key.

        If any of the levels are new, they are created along the
        way.
        """
        if self._locked:
            cls = type(self).__name__
            raise ValueError(f'Unable to set {key!r} on locked {cls}')
        role, attr, ref = self._check_key(key)
        role_map = self.__dict__['_mapping']
        if role not in role_map:
            role_map[role] = {}
        attr_map = role_map[role]
        if attr not in attr_map:
            attr_map[attr] = {}
        ref_map = attr_map[attr]
        ref_map[ref] = value

    def __contains__(self, key):
        """
        Checks if this mapping has the specified partial key.

        Key may be a single string or a :py:class:`tuple` with a length
        between 1 and 3. Checks will be made for the appropriate depth.
        """
        role_map = self.__dict__['_mapping']
        if isinstance(key, str):
            return key in role_map
        elif not isinstance(key, tuple) or 3 < len(key) <= 0:
            raise TypeError('Containment check only allowed for role (str) '
                            'or partial keys (tuple)')
        role = key[0]
        if role not in role_map:
            return False
        if len(key) == 1:
            return True
        attr_map = role_map[role]
        attr = key[1]
        if attr not in attr_map:
            return False
        if len(key) == 2:
            return True
        ref_map = attr_map[attr]
        ref = key[2]
        return ref in ref_map

    def __str__(self, indent=2):
        """
        Creates a pretty representation of this map, with indented
        heading levels.
        """
        role_map = self.__dict__['_mapping']
        output = StringIO()
        indent1 = ' ' * indent
        indent2 = 2 * indent1
        indent3 = 3 * indent1
        output.write(f'{type(self).__name__}(\n')
        for role, attr_map in role_map.items():
            output.write(f'{indent1}role = {role!r}: {{\n')
            for attr, ref_map in attr_map.items():
                output.write(f'{indent2}attribute = {attr!r}: {{\n')
                for ref, value in ref_map.items():
                    output.write(f'{indent3}key = {ref!r}: "{value}"\n')
                output.write(f'{indent2}}}\n')
            output.write(f'{indent1}}}\n')
        output.write(')\n')
        return output.getvalue()

    def lock(self):
        """
        Lock this mapping to prevent unintentional modification.

        This is a one-time operation. There is no way to unlock.
        After locking, :py:meth:`__setitem__` will raise an error.
        """
        self._locked = True

    @staticmethod
    def _check_key(key):
        """
        Verify that the supplied key is valid to index this map, raise
        a :py:exc:`TypeError` if not.

        This utility just checks that the key is a 3-element
        :py:class:`tuple` of strings.
        """
        if not isinstance(key, tuple) or len(key) != 3:
            raise TypeError('Key of the form (role, attribute, key) required')
        if not all(isinstance(x, str) for x in key):
            raise TypeError('Only strings allowed in key')
        return key


class _StateBase:
    """
    The base container type for the states of the different phases of
    the :ref:`introduction-layers-engine`.

    This class abstracts the common functionality used by all the engine
    components. It allows for a containment check using ``in`` in
    preferece to :py:func:`hasattr`.

    .. py:attribute:: references

       :py:class:`ReferenceMap`

       A multi-level mapping type that allows references to be fetched
       by role and attribute. Access to this map is performed by
       providing a tuple ``(role, attribute, key)``. For example::

           state.references['figure', 'id', 'my_figure']

       The map's values may be of any type, as long as they can be
       converted to the desired content using :py:class:`str`.

       Implemented as a read-only property.
    """
    def __init__(self, references, log):
        self.__dict__.update(
            references=references,
            log=log,
        )

    def __contains__(self, name):
        """
        Checks if the specified name represents an attribute.
        """
        return hasattr(self, name)

    @property
    def references(self):
        """
        Ensure that :py:attr:`references` is read-only.
        """
        return self.__dict__['references']

    def log(self, lvl, msg, *args, **kwargs):
        """
        Provide access to the engine's logging facility.

        Usage is analagous to :py:func:`logging.log`. XML location
        meta-data will be inserted into any log messages.
        """
        # This method is actually just a placeholder for the documentation.
        # It gets overriden by a bound method passed in to the constructor.
        pass

    def get_content(self, default=''):
        """
        Retrieve the text in the current :py:attr:`content` buffer.

        Whitespace is stripped from each line in the text, which is then
        recombined with spaces instead of newlines.

        If the buffer is non-existent, empty or contains only
        whitespace, return `default` instead.
        """
        if 'content' not in self:
            return default
        text = aggressive_strip(self.content.getvalue())
        if not text:
            text = default
        return text


class ReferenceState(_StateBase):
    """
    A simple container type used by the reference parser to communicate
    state to the reference descriptors and accumulate the reference map.

    Most of the state is dedicated to monitoring referenceable tags and
    creating references to them. The engine and built-in tags rely on a
    set of attributes to function properly. A description of acceptable
    use of these attributes is provided here. Any other use may lead to
    unexpected behavior. Custom tags may define and use any attributes
    that are not explicitly documented as they chose.

    This class allows for a containment check using ``in`` in preferece
    to :py:func:`hasattr`.

    .. py:attribute:: registry

       ``Mapping``

       A subtype of :py:class:`dict` that follows the same rules as
       :py:data:`~imprint.core.tags.tag_registry`. Normally a reference
       to that attribute.

       Implemented as a read-only property.

    .. py:attribute:: references

       :py:class:`ReferenceMap`

       A multi-level mapping type that allows references to be fetched
       and set by role and attribute. Access to this map is performed by
       providing a tuple ``(role, attribute, key)``. For example::

           state.references['figure', 'id', 'my_figure']

       The map's values may be of any type, as long as they can be
       converted to the desired content using :py:class:`str`.

       The map is mutable at this stage in the processing. It
       accumulates all the referenceable tags found in the document.
       Setting a value for a key any of whose levels do not exist is
       completely acceptable: the missing levels will be filled in.

       Implemented as a read-only property.

    .. py:attribute:: heading_depth

       :py:class:`int`

       The configured depth after which :py:attr:`heading_counter` stops
       having an effect when a subheading is entered. If omitted
       entirely (:py:obj:`None`), all available heading levels will be
       used.

       Implemented as a writable property.

    .. py:attribute:: heading_counter

       :py:class:`list`\ [\ :py:class:`int`\ ]

       A list containing counters for each heading level encountered.
       The list is popped back one element whenever a higher level
       heading is encountered. ``len(heading_counter)`` is the depth of
       the outline the parser is currently in. E.g., if the parser is
       parsing text under ``Section 3.4.5``, ``heading_counter``
       contains ``[3, 4, 5]``. When ``Section 4`` is encountered next,
       the counter will be reset to ``[4]``. The heading may be
       referenced later by title or by ID.

       A :py:class:`~collections.deque` is not used because it does not
       support slice deletion, which makes jumping back a few heading
       levels much easier.

       Implemented as a read-only property.

    .. py:attribute:: item_counters

       :py:class:`dict`\ [\ :py:class:`str` -> :py:class:`int`\ ]

       A mapping of the :term:referenceable roles to the counters of
       items in the current heading. All the counters are reset to zero
       when a new heading below :py:attr:`heading_depth` is encountered.

       Implemented as a read-only property. The keys of the mapping
       should not be modified, but the values may be.

    .. py:attribute:: content

       :py:class:`io.StringIO`

       A mutable buffer used by the engine to accumulate text from the
       :ref:`configuration-xml` only when necessary.

       This attribute should be manipulated mostly through the
       :py:meth:`start_content` and :py:meth:`end_content` methods. It
       should only be present for tags that care about accumulating
       content for a reference, like :ref:`xml-spec-tags-par`. When
       present, all content, regardless of nested tags, will be
       accumulated.
    """
    def __init__(self, registry, log, heading_depth=None):
        super().__init__(references=ReferenceMap(), log=log)
        self.__dict__.update(
            registry=registry,
            heading_counter=[],
            item_counters={key: 0 for key in registry.referable_tags},
        )
        self.heading_depth = heading_depth

    @property
    def registry(self):
        """
        Ensure that :py:attr:`registry` is read-only.
        """
        return self.__dict__['registry']

    @property
    def heading_counter(self):
        """
        Ensure that :py:attr:`heading_counter` is read-only.
        """
        return self.__dict__['heading_counter']

    @property
    def item_counters(self):
        """
        Ensure that :py:attr:`item_counters` is read-only.
        """
        return self.__dict__['item_counters']

    @property
    def heading_depth(self):
        """
        Ensure that :py:attr:`heading_depth` is set to a legitimate
        value.
        """
        return self.__dict__['heading_depth']

    @heading_depth.setter
    def heading_depth(self, depth):
        if depth is not None:
            depth = index(depth)
            if depth < 0:
                raise ValueError('Negative heading_depth')
        self.__dict__['heading_depth'] = depth

    def start_content(self):
        """
        Create a new :py:attr:`content` buffer.

        If a buffer already exists, a warning is issued (even if it is
        empty), and its contents are discarded.
        """
        if 'content' in self:
            self.log(logging.WARNING, 'Creating duplicate content buffer')
        self.content = StringIO()

    def end_content(self):
        """
        Terminate the current content buffer, if any, and return the
        content after aggressive stripping of whitespace.

        If there is no :py:attr:`content` buffer to begin with, an empty
        string is returned.
        """
        text = self.get_content()
        del self.content
        return text

    def reset_counters(self):
        """
        Set all the values of :py:attr:`item_counters` to zero.
        """
        for key in self.item_counters:
            self.item_counters[key] = 0

    def increment_heading(self, level):
        """
        Increment :py:attr:`heading_counter` at the requested `level`.

        Any missing levels are set to 1 with a warning. Any further
        levels are truncated. :py:attr:`item_counters` is reset if
        :py:attr:`heading_depth` is unset or a greater value than
        `level`.
        """
        if level < 0:
            raise ValueError(f'Negative level {level}')

        self.log(logging.DEBUG, 'Found heading with level %d', level)
        current_level = len(self.heading_counter)

        # Another subheading on the same level
        if level == current_level:
            self.heading_counter[-1] += 1
            self.log(logging.INFO, 'Entered section %s '
                     '(mainained subsection level)', self.format_heading())

        # New subheading: only one level of depth increase allowed at a time
        elif level > current_level:
            diff = level - current_level
            if diff == 1:
                self.heading_counter.append(1)
                self.log(logging.DEBUG, 'Entered section %s '
                         '(subsection level increased to %d)',
                         self.format_heading(), level)
            else:
                self.heading_counter.extend(repeat(1, diff))
                self.log(logging.WARNING, 'Suspicious heading level: '
                         'jumping from depth %d to %d', current_level, level)

        # Jump back to higher level heading
        else:
            del self.heading_counter[level:]
            self.heading_counter[-1] += 1
            self.log(logging.DEBUG, 'Jumped back to parent section %s '
                     '(from depth %d to %d)', self.format_heading(),
                     current_level, level)

        if self.heading_depth is None or level <= self.heading_depth:
            self.reset_counters()
            if self.heading_depth is None:
                msg = 'unlimited depth'
            else:
                msg = f'level={level} <= depth={self.heading_depth}'
            self.log(logging.DEBUG, 'Reset item counters (%s)', msg)
        else:
            self.log(logging.DEBUG, 'Item counters will not be reset '
                     '(level=%d > depth=%d', level, self.heading_depth)

    def format_heading(self, prefix=None, prefix_sep=' ', sep='.',
                       suffix_sep='-', suffix=None):
        """
        Format :py:attr:`heading_counter` for display.

        If `suffix` is set to a Truthy value, only
        :py:attr:`heading_depth` items are shown. Otherwise, the entire
        list is shown.
        """
        depth = self.heading_depth
        if depth is None or not suffix:
            depth = len(self.heading_counter)
        heading = sep.join(map(str, self.heading_counter[:depth]))

        if not prefix:
            prefix = prefix_sep = ''
        if not suffix:
            suffix = suffix_sep = ''
        elif not heading:
            suffix_sep = ''

        return f'{prefix}{prefix_sep}{heading}{suffix_sep}{suffix}'


@unique
class ListType(Enum):
    """
    The type of list numbering to use for :ref:`xml-spec-tags-par` tags
    that require it.
    """

    #: Start a new numbered list.
    NUMBERED = 'numbered'

    #: Start a new bulleted list.
    BULLETED = 'bulleted'

    #: Continue with the numbering/bullets of an existing list.
    CONTINUED = 'continued'

    @classmethod
    def convert(cls, value):
        """
        Normalize the provided value, or raise a :py:exc:`ValueError`.

        Values are assigned based on the case-insensitive prefix that
        they represent. `value` must be a string.
        """
        cvalue = value.casefold()
        for e in cls:
            if e.value.startswith(cvalue):
                return e
        else:
            raise ValueError(f'Illegal value of {cls.__name__} {value!r}')


class EngineState(_StateBase):
    """
    A simple container type used by the main parser to communicate
    document state to the tag descriptors.

    Most of the state is dedicated to monitoring the status of the text
    acquisition from the XML. The engine and built-in tags rely on a set
    of attributes to function. A description of acceptable use of these
    attributes is provided here. Any other use may lead to unexpected
    behavior. Custom tags may define and use any attributes that are not
    explicitly documented as they choose.

    This class allows for a containment check using ``in`` in preferece
    to :py:func:`hasattr`.

    .. py:attribute:: doc

       :py:class:`docx.document.Document`

       The document that is being built. Set once by the engine.

       Implemented as a read-only property.

    .. py:attribute:: keywords

       :py:class:`dict`

       The keywords configured for this document by the
       :ref:`configuration-ipc`. Normally, this dictionary should be
       treated as read-only, but :py:class:`~imprint.core.tags.ExprTag`
       can add new entries.

       As a rule, keywords with lowercase names are system configuration
       options, while keywords that start with upper case letters affect
       document content.

       Implemented as a read-only property.

    .. py:attribute:: references

       :py:class:`ReferenceMap`

       A multi-level mapping type that allows references to be fetched
       by role and attribute. Access to this map is performed by
       providing a tuple ``(role, attribute, key)``. For example::

           state.references['figure', 'id', 'my_figure']

       The map's values may be of any type, as long as they can be
       converted to the desired content using :py:class:`str`.

       The mapping is made immutable as soon as it becomes part of the
       state. The read-only lock is irreversible.

       Implemented as a read-only property.

    .. py:attribute:: paragraph

       :py:class:`docx.text.paragraph.Paragraph`

        A paragraph represents a collection of runs and other objects
        that make up a logical segment in a document. This attribute
        exists only when parsing a :ref:`xml-spec-tags-par` tag. Usually
        set and unset by :py:class:`~imprint.core.tags.ParTag`, but can
        be temporarily switched off and reinstated in response to other
        tags as well. :py:meth:`end_paragraph` deletes this attribute.

    .. py:attribute:: run

       :py:class:`docx.text.run.Run`

        A run is a collection of characters with similar formatting
        within a paragraph. This attribute exists only when parsing a
        :ref:`xml-spec-tags-run` tag. Usually set and unset by
        :py:class:`~imprint.core.tags.RunTag`. :py:meth:`end_paragraph`
        deletes this attribute.

    .. py:attribute:: content

       :py:class:`io.StringIO`

       A mutable buffer used by the engine to accumulate text from the
       :ref:`configuration-xml`.

       Since whitespace needs to be trimmed rather aggressively from
       an XML file, this object gets an extra (non-standard) attribute:

       .. py:attribute:: content.leading_space

          Indicates whether or not to prepend a space when concatenating
          this buffer with others. In general, the text of the first run
          in a paragraph is the only one that does not have this
          attribute set to :py:obj:`True`. This flag is set on the
          buffer rather than the state object itself so that buffers can
          be pushed and popped into the :py:attr:`.content_stack` to
          handle nested tags.

       This attribute should be manipulated mostly through the
       :py:meth:`new_content`, :py:meth:`get_content` and
       :py:meth:`flush_run` methods.

       This attribute must always be present, regardless of the
       position within the document.

       Implemented as a read-write property that can not be deleted or
       set to :py:obj:`None`.

    .. py:attribute:: content_stack

       :py:class:`collections.deque`\ [\ :py:class:`io.StringIO`\ ]

       A stack for nested content buffers. Each buffer represents a tag
       containing independent content. Some tags append to the parent's
       buffer, some close the current buffer to start a new one and
       others, such as :ref:`xml-spec-tags-figure`, use a temporary
       buffer for their content.

       The stack allows for a theoretically indefinite level of nesting
       of text elements. In reality, it will only contain one or two
       elements: the current run text and the contents of interpersed
       tags like :ref:`xml-spec-tags-figure`.

       This attribute should be maniplated through the
       :py:meth:`push_content_stack` and :py:meth:`pop_content_stack`
       methods.

       This attribute may be empty, but never missing. Implemented as a
       read-only property.

    .. py:attribute:: last_list_item

       :py:class:`docx.text.paragraph.Paragraph`

       List items in Word are just paragraphs with a particular style
       and numbering scheme. All of this information can be gathered
       from the previous paragraph that was assigned a concrete list
       numbering instance.

       This attribute should never be missing. It should only be
       :py:obj:`None` to indicate that no prior numbered paragraph has
       occured in the document yet. To this end, it is implemented as a
       read-only property.

    .. py:attribute:: latex_count

       :py:class:`int`

       A counter for the number of :ref:`xml-spec-tags-latex` tags
       encountered so far. Used to generate the file name for the
       equations if :ref:`logging-images` is enabled. Missing otherwise.
    """
    def __init__(self, doc, keywords, references, log):
        """
        Create a new namespace with the specified named arguments.
        """
        references.lock()  # Ensure that this happens no matter what
        super().__init__(references=references, log=log)
        self.__dict__.update(
            doc=doc,
            keywords=keywords,
            content_stack=deque(),
            last_list_item=None,
        )
        self.new_content(False)

    @property
    def doc(self):
        """
        Ensure that :py:attr:`doc` is read-only.
        """
        return self.__dict__['doc']

    @property
    def keywords(self):
        """
        Ensure that :py:attr:`keywords` is read-only.
        """
        return self.__dict__['keywords']

    @property
    def content(self):
        """
        Ensure that :py:attr:`content` is set to a valid
        :py:class:`io.StringIO`.

        Assign a :py:attr:`~content.leading_space` attribute to it if
        not already set.
        """
        return self.__dict__['content']

    @content.setter
    def content(self, value):
        """
        Check the type and ensure that :py:attr:`~content.leading_space`
        is assigned.
        """
        if not isinstance(value, StringIO):
            raise TypeError('Content may only be an io.StringIO object. '
                            'Found {type(value).__name__}')
        if not hasattr(value, 'leading_space'):
            value.leading_space = self.__dict__['content'].leading_space
        self.__dict__['content'] = value

    @property
    def content_stack(self):
        """
        Ensure that :py:attr:`content_stack` is read-only.
        """
        return self.__dict__['content_stack']

    @property
    def last_list_item(self):
        """
        Ensure that :py:attr:`last_list_item` does not get accidentally
        deleted.
        """
        return self.__dict__['last_list_item']

    @last_list_item.setter
    def last_list_item(self, value):
        self.__dict__['last_list_item'] = value

    def new_content(self, leading_space=None):
        """
        Update the :py:attr:`content` text buffer to a new, empty
        :py:class:`~io.StringIO`.

        Calling this method is faster than doing a seek-truncate
        according to http://stackoverflow.com/a/4330829/2988730.

        Parameters
        ----------
        leading_space : tri-state bool
            If :py:obj:`None`, copy :py:attr:`~content.leading_space`
            from the current :py:attr:`content`. Otherwise, set to the
            provided value. The default is to copy the existing value.
        """
        new = StringIO()
        if leading_space is None:
            new.leading_space = self.content.leading_space
        else:
            new.leading_space = bool(leading_space)
        self.content = new

    def get_content(self, default=''):
        """
        Retrieve the text in the current :py:attr:`content` buffer.

        Whitespace is stripped from each line in the text, which is then
        recombined with spaces instead of newlines.

        If the buffer is empty (or contains only whitespace), return
        `default` instead.

        If the text is non-empty, and :py:attr:`content` has
        :py:attr:`~content.leading_space` set to :py:obj:`True`,
        prepended a space.
        """
        text = super().get_content(default)
        # Prepend a leading space to non-empty values that request it.
        if text and self.content.leading_space:
            text = ' ' + text
            #self.content.leading_space = False
                # Pretty sure this should not be done: if content is not
                # removed, neither should the leading white-space be. Possible
                # that it is done for next call to renew not to set the leading
                # whitespace?
        return text

    def flush_run(self, renew=True, default=''):
        """
        Flush the text buffer accumulating the current run into the
        document.

        Text flushing aggressively removes whitespace from around
        individual lines. A single space character is prepended
        before the text if :py:attr:`content.leading_space` is
        :py:obj:`True`.

        If not inside a run, this is a no-op.

        Parameters
        ----------
        renew : bool
            Whether or not to create a new text buffer when finished.
            This is generally a good idea, since the content will
            already be in the document, so the default is
            :py:obj:`True`. The new buffer has
            :py:attr:`~content.leading_space` set to :py:obj:`True`.
        default : str
            The text to insert if the current :py:attr:`content` buffer
            is empty. Defaults to nothing (``''``).
        """
        if 'run' in self:
            text = self.get_content(default)
            if text:
                self.run.add_text(text)
            if renew:
                # Add a space between content, don't add a space otherwise
                space = True if self.run.text else None
                self.new_content(space)

    def push_content_stack(self, flush=False, leading_space=False):
        """
        Temporarily create a new text buffer for the :py:attr:`content`.

        If ``flush`` is :py:obj:`True`, the old buffer is flushed to
        the document and cleared before being pushed to the
        :py:attr:`content_stack`. If ``flush`` is :py:obj:`False`, the
        existing buffer is pushed unchanged. If the content is flushed,
        its :py:attr:`~content.leading_space` attribute is set to
        :py:obj:`True`.

        If the existing buffer is flushed, the buffer that will be
        reinstated when the new one is popped will have
        :py:attr:`~content.leading_space` set to :py:obj:`True`.

        The new buffer can have its :py:attr:`~content.leading_space`
        attribute configured by the ``leading_space`` parameter, which
        defaults to :py:obj:`False`.
        """
        if flush:
            self.flush_run()
        self.content_stack.append(self.content)
        self.new_content(leading_space)
        self.log(logging.TRACE, 'Pushed content stack one level to %d',
                 len(self.content_stack))

    def pop_content_stack(self):
        """
        Reinstate the previous level of the :py:attr:`content_stack` to
        the current :py:attr:`content`.

        Calling this method on an empty stack will cause an error. The
        current :py:attr:`content` is completely discarded.
        """
        self.content = self.content_stack.pop()
        self.log(logging.TRACE, 'Popped content stack one level to %d',
                 len(self.content_stack))

    def check_content_tail(self):
        """
        Include any remaining text in :py:attr:`content` into the last
        run of the last paragraph.

        This ensures that paragraphs get truncated properly, and that
        spurious text between paragraphs is cleaned up.

        A warning is issued if any non-whitepace text is found.
        """
        tail = self.get_content()
        if tail:
            self.log(logging.WARNING, 'Found spurious content outside of run')
            if 'paragraph' in self:
                self.log(logging.TRACE, 'Spurious text within paragraph')
                if self.paragraph.runs:
                    self.log(logging.TRACE, 'Appending to last run')
                    self.paragraph.runs[-1].add_text(tail)
                else:
                    self.log(logging.TRACE, 'Creating new run')
                    self.paragraph.add_run(tail, style=defaults.run_style)
            else:
                self.log(logging.TRACE,
                         'Spurious text outside paragraph: adding a new one')
                paragraph = self.doc.add_paragraph(style=defaults.paragraph_style)
                paragraph.add_run(tail, style=defaults.run_style)
        else:
            self.log(logging.TRACE, 'No content outside run')

        # Make sure the new conent does not have a leading space.
        self.new_content(False)

    def new_run(self, tag, style=defaults.run_style,
                pstyle=defaults.paragraph_style,
                check_in_par=True, keep_par=True):
        """
        Create a new :py:attr:`run`.

        This method handles cases when a run is requested outside a
        paragraph, or inside an existing run:

        - Nested runs are forbidden, but run injection is not.

          - Existing content is flushed for injected runs.

        - Runs outside a paragraph will generate a temporary paragraph
          with a default style.

          - Missing paragraphs can optionally raise a warning.
          - The temporary paragraph can optionally be retained as the
            current paragraph.

        Parameters
        ----------
        name : str
            The name of the tag requesting the run. If there is already
            a :py:attr:`run` attribute present, setting ``name='run'``
            will raise an error because of nesting.
        style : str
            The name of the style to use for the new run.
        pstyle : str
            The name of the style to use for a new paragraph, if one has
            to be created. Moot if there is already a
            :py:attr:`paragraph` attribute.
        check_in_par : bool
            Whether or not to warn if not in a paragraph. Defaults to
            :py:obj:`True`.
        keep_par : bool
            Whether or not to retain a newly created paragraph object in
            the :py:attr:`paragraph` attribute. Moot if there is already
            a :py:attr:`paragraph` attribute.

        Return
        ------
        par : docx.text.paragraph.Paragraph
            The paragraph that the run was added to. If ``keep_par`` is
            :py:obj:`True` or there was already a :py:attr:`paragraph`
            attribute set, this will be the :py:attr:`paragraph`
            attribute.
        run : docx.run.Run
            The newly created run. This will be set to the
            :py:attr:`run` attribute unless there is no existing
            :py:attr:`paragraph` attribute, and ``keep_par`` is set to
            :py:obj:`False`.

        Notes
        -----
        Setting ``keep_par`` to ``False`` for a :ref:`xml-spec-tags-run`
        tag outside a paragraph will cause a situation where
        :py:attr:`run` is set but :py:attr:`paragraph` is not. This may
        cause a problem for the engine, but should never arise with the
        builtin parsers.
        """
        if 'run' in self:
            if tag is not None and tag.casefold() == 'run':
                msg = 'Nested runs are forbidden!'
                self.log(logging.ERROR, msg)
                raise SyntaxError(msg)
            else:
                self.log(logging.DEBUG, 'Run injection detected: <%s>', tag)
                self.flush_run()
        else:
            if 'paragraph' in self:
                space = not is_paragraph_empty(self.paragraph)
            else:
                space = False
            self.new_content(space)

        if 'paragraph' not in self:
            if check_in_par:
                self.log(logging.WARNING, 'Found <%s> outside of <par>', tag)
            paragraph = self.doc.add_paragraph(style=pstyle)
            if keep_par:
                self.paragraph = paragraph
        else:
            paragraph = self.paragraph
        run = paragraph.add_run(style=style)
        if paragraph is self.paragraph:
            self.run = run
        return paragraph, run

    def end_paragraph(self, tag=None):
        """
        Terminate the current paragraph.

        Any existing run is immediately terminated. Spurious text is
        appended to the last available run. Both :py:attr:`paragraph`
        and :py:attr:`run` attributes are deleted by this method.

        If there is no paragraph to terminate, this method is
        equivalent to calling :py:meth:`check_content_tail`.

        Parameters
        ----------
        tag : str or None
            The name of a tag that interrupts the paragraph. If present,
            a warning will be issued. If omitted, no warning will be
            issued.
        """
        self.check_content_tail()
        if 'paragraph' in self:
            if is_paragraph_empty(self.paragraph):
                self.log(logging.DEBUG, 'Found unused paragraph. '
                         'Removing completely.')
                delete_paragraph(self.paragraph)

            del self.paragraph

            if tag is not None:
                self.log(logging.WARNING, '<%s> found in paragraph. '
                         'Paragraph terminated', tag)

        if 'run' in self:
            # Remember that check_content_tail has already appended to the run.
            self.log(logging.WARNING,
                     'Suspicious unterminated run closed with paragraph')
            del self.run

        self.log(logging.TRACE, 'Ended paragraph')

    def insert_picture(self, img, flush_existing=True,
                       style=defaults.figure_run_style,
                       pstyle=defaults.figure_paragraph_style,
                       **kwargs):
        """
        Insert an image into the current document.

        Images must be inserted into a run, so the following cases are
        recognized:

        Outside :ref:`xml-spec-tags-par`
            Create a new temporary
            :py:class:`~docx.text.paragraph.Paragraph` and a new
            :py:class:`~docx.text.run.Run`. Neither object is retained
            (i.e. in :py:attr:`paragraph` and :py:attr:`run`).
        Inside :ref:`xml-spec-tags-par` but outside :ref:`xml-spec-tags-run`
            Create a new temporary :py:class:`~docx.text.run.Run`, which
            will not be retained.
        Inside :ref:`xml-spec-tags-run`
            If the requested ``style`` matches the style of the current
            :py:attr:`run`, it will be flushed and extended. Otherwise,
            the current :py:attr:`run` will be interrupted by a
            temporary run with the new style, and then reinstated.

        It is an error to have a run outside a paragraph.

        Parameters
        ----------
        img : str or file-like
            The image can be the name of a file on disk, or an open file
            (including in memory files like :py:class:`io.BytesIO`). In
            the latter case, the file pointer must be at the beginning
            of the image data.
        style : str
            The name of the
            :doc:`dev/analysis/features/styles/character-style` to apply
            to a new run.
        pstyle : str
            The name of the
            :doc:`dev/analysis/features/styles/paragraph-style` to apply
            if a new paragraph needs to be created.


        Two additional keyword-only arguments can be supplied to
        :py:meth:`~docx.text.run.Run.add_picture`: ``width`` and
        ``height``.
        """
        with self.temp_run(style=style, pstyle=pstyle, keep_same=True):
            pic = self.run.add_picture(img, **kwargs)
        self.log(logging.DEBUG, 'Inserted %s"x%s" picture (WxH)',
                 pic.width.inches, pic.height.inches)

    def inject_par(self, style=defaults.run_style,
                   pstyle=defaults.paragraph_style, text=''):
        """
        Insert a new paragraph into the document with the specified
        styles and text, and return it.

        The contents of the paragraph will be a single run with the
        specified text. Any previously existing :py:attr:`paragraph` and
        :py:attr:`run` will be terminated (see :py:meth:`end_paragraph`)
        and reinstated with their proir styles once the new content is
        inserted.

        Parameters
        ----------
        style : str
            The name of the character style to use for the inserted run.
        pstyle : str
            The name of the paragraph style to apply to the new
            paragraph.
        text : str
            The optional text to insert into the new run.

        Return
        ------
        par : docx.text.paragraph.Paragraph
            The newly created paragraph. This will be a temporary object
            that is never set as :py:attr:`paragraph`.
        run : docx.run.Run
            The newly created run. This will be a temporary object that
            is never set as :py:attr:`run`.
        """
        with self.interrupt_paragraph():
            self.log(logging.DEBUG, 'Injecting par(pstyle=%s, style=%s)',
                     pstyle, style)
            par = self.doc.add_paragraph(style=pstyle)
            run = par.add_run(style=style, text=text)
        return par, run

    @contextmanager
    def temp_run(self, style=defaults.run_style,
                 pstyle=defaults.paragraph_style, keep_same=False):
        """
        Create a temporary run in the current context.

        The run and paragraph styles will be preserved after the context
        manager exits. If the run is injected outside a paragraph, a
        temporary paragraph will be created and forgotten.

        Within the context manager, both :py:attr:`paragraph` and
        :py:attr:`run` are guaranteed to be set to be set. :py:attr:`run`
        will have the style named by ``style``, but :py:attr:`paragraph`
        will only have the style named by ``pstyle`` if it is a
        temporary paragraph.

        All content is flushed into the temporary run when this manager
        exits.

        Parameters
        ----------
        style : str
            The style of the new run.
        pstyle : str
            The style of a new paragraph to contain the run. Used only
            if :py:attr:`paragraph` is unset.
        keep_same : bool
            If :py:obj:`True`, and a run already exists, and has the
            same style as this one, retain it instead of making a new
            one. If :py:obj:`False` (the default), always create a new
            run.
        """
        # Retain old paragraph and run objects
        old_run = self.run if 'run' in self else None
        old_par = self.paragraph if 'paragraph' in self else None

        # Check that keep_same is not activated
        if keep_same and old_run is not None and old_run.style.name == style:
            self.log(logging.DEBUG, 'Not injecting run(style=%s): same style '
                     'as existing', style)
            self.flush_run()
        else:
            if 'run' in self:
                msg = f'into run(style={old_run.style.name})'
            else:
                msg = 'by itself'
            self.log(logging.DEBUG, 'Injecting run(style=%s) %s', style, msg)
            self.new_run(None, style=style, pstyle=pstyle,
                         check_in_par=False, keep_par=True)

        # Do context-manager stuff
        yield

        # Reinstate prior styles
        self.flush_run()
        if self.paragraph is not old_par:
            if 'run' in self:
                del self.run
            self.end_paragraph()
            if old_par is not None:
                self.paragraph = self.doc.add_paragraph(style=old_par.style)
                if old_run is not None:
                    self.run = self.paragraph.add_run(style=old_run.style)
                    self.new_content(False)
        else:
            if old_run is None:
                del self.run
            elif self.run is not old_run:
                self.run = self.paragraph.add_run(style=old_run.style)


    @contextmanager
    def interrupt_paragraph(self, warn=None):
        """
        A context manager for interrupting the current run/paragraph
        and resuming it when complete.

        The current paragraph and run are ended before the body of the
        ``with`` block executes. They are reinstated afterwards, if they
        existed to begin with, with the same styles as before.

        Parameters
        ----------
        warn : str, bool or None
            If a boolean, determines whether or not to issue a generic
            warning if a paragraph is actually interrupted. If a string,
            it is interpreted as the name of the tag that is
            interrupting the paragraph, and mentioned in the warning. No
            warning will be issued if falsy. Defaults to :py:obj:`None`.
        """
        if 'paragraph' in self:
            if 'run' in self:
                style = (self.paragraph.style, self.run.style)
                what = 'run'
                where = '(pstyle=%s, rstyle=%s)'
            else:
                style = (self.paragraph.style,)
                what = 'paragraph'
                where = '(pstyle=%s)'

            if not warn:
                level = logging.DEBUG
                prefix = ''
            else:
                level = logging.WARNING
                prefix = '' if warn is True else f'{warn} inside {what}: '

            self.log(level, '%sInterrupting %s ' + where,
                     prefix, what, *(s.name for s in style))
            self.end_paragraph()
        else:
            style = ()
            self.log(logging.DEBUG, 'Not interrupting anything')

        yield

        if style:
            insert = f'after {warn}' if warn and not isinstance(warn, bool) \
                        else ''
            self.log(logging.TRACE, 'Reinstating paragraph %s with style=%r',
                     insert, style[0])
            self.paragraph = self.doc.add_paragraph(style=style[0])
            if len(style) > 1:
                self.log(logging.TRACE, 'Reinstating run %sstyle=%r', style[1])
                self.run = self.paragraph.add_run(style=style[1])

    def number_paragraph(self, list_type, level):
        """
        Turn the current paragraph into a list item, and store it into
        :py:attr:`last_list_item`.

        The exact numbering scheme depends on :py:attr:`last_list_item`,
        which will be updated to refer to the current paragraph when
        this method completes.

        The following behaviors occur in response to ``list_type``:

        +--------------------------------+---------------------------------+
        | ``list_type``                  | Behavior                        |
        +================================+=================================+
        | :py:obj:`None`                 | Not a list paragraph. Do not    |
        |                                | set numbering or change         |
        |                                | :py:attr:`last_list_item`.      |
        +--------------------------------+---------------------------------+
        | :py:attr:`~ListType.CONTINUED` | Same type and numbering as      |
        |                                | :py:attr:`last_list_item`.      |
        |                                | Set :py:attr:`last_list_item`.  |
        +--------------------------------+---------------------------------+
        | :py:attr:`~ListType.NUMBERED`  | Start a new numbered list.      |
        |                                | Set :py:attr:`last_list_item`.  |
        +--------------------------------+---------------------------------+
        | :py:attr:`~ListType.BULLETED`  | Start a new numbered list.      |
        |                                | Set :py:attr:`last_list_item`.  |
        +--------------------------------+---------------------------------+

        Parameters
        ----------
        list_type : ListType or None
            The type of list to number with, if at all.
        level : int or None
            The depth of the list indentation. :py:obj:`None` means to
            follow the level of the previous list item, if any, or use
            zero depth.
        """
        if list_type is None or 'paragraph' not in self:
            return

        if list_type is ListType.CONTINUED:
            self.log(logging.TRACE, 'Continuing existing list')
            prev = self.last_list_item
            num = None
            if prev is None:
                self.log(logging.WARNING, 'Attempting to continue a list '
                         'when no list exists')
                num = True
        else:
            self.log(logging.TRACE, 'Starting %s list', list_type.value)
            prev = None
            if list_type is ListType.NUMBERED:
                num = True
            elif list_type is ListType.BULLETED:
                num = False
            else:
                raise ValueError(f'Unsupported ListType {list_type!r}')

        list_number(self.doc, self.paragraph, prev, level, num)
        self.last_list_item = self.paragraph

    def image_log_name(self, id, ext=''):
        """
        Create an output name to log an image (or data), for a
        :ref:`plugins-data-configuration` with the given ID, and an
        optional extension.

        This is the standard name-generator for any component (
        :ref:`tag descriptor <tag-api-descriptors>` or
        :ref:`plugin handler <plugins-handlers>`) that enables image
        logging in response to :ref:`keywords-system-log_images`.

        The base name is the result of concatenating an extension-less
        :ref:`keywords-system-log_file` (or
        :ref:`keywords-system-output_docx` if not set), with ``id``,
        separated by an underscore. ``ext`` is appended as-is, if
        provided.
        """
        # select the log file if possible, the output document if not.
        base = self.keywords.get('log_file')
        if not isinstance(base, str):
            base = self.keywords['output_docx']
        path = abspath(base)
        fname, _ = splitext(path)
        return f'{fname}_{id}{ext}'
