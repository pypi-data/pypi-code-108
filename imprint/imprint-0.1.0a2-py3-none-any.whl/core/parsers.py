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
:py:mod:`imprint.core.parsers` implements the parsers used to process the
:ref:`configuration-xml`. These parsers make up the heart of the
:ref:`introduction-layers-engine`.

There are currently two parsers: :py:class:`ReferenceProcessor` and
:py:class:`TemplateProcessor`. Both are instances of
:py:class:`haggis.files.xml.SAXLoggable`. The former creates a table of
reference names/titles/locations/numbers that are used by the the latter.
"""

__all__ = ['ReferenceProcessor', 'TemplateProcessor', 'RootTag']


from collections import deque
import logging
import pprint

from haggis.load import module_as_dict
from haggis.files.xml import SAXLoggable
from haggis.files.docx import is_paragraph_empty, delete_paragraph

from . import root_tag, KnownError
from . import defaults
from .tags import TagDescriptor, tag_registry
from .state import ReferenceState, EngineState


class OpenTagError(Exception):
    """
    Used as a goto+label marker when processing opening tags.

    As per https://stackoverflow.com/a/41768438/2988730 and
    https://docs.python.org/3/faq/design.html#why-is-there-no-goto

    This error is raised to indicate a non-fatal error that prevents
    the closing tag from being processed.
    """
    pass


class TagStackNode:
    """
    A structure for maintaining information about open tags for
    :py:class:`TemplateProcessor`.

    All of the attributes except :py:attr:`warned` are immutable, so
    while tempting, a :py:func:`~collections.namedtuple` can not be used.

    All attributes are passed to the constructor in the same order that
    they are listed here. Only the first two are required.

    .. py:attribute:: name

       The name of the tag, not normalized in any way.

    .. py:attribute:: attr

       A plain :py:class:`dict` containing the
       :py:attr:`~imprint.core.tags.TagDescriptor.required` and
       :py:attr:`~imprint.core.tags.TagDescriptor.optional` attributes
       of the tag. This attribute is mutable and gets passed to both the
       :py:meth:`~imprint.core.tags.TagDescriptor.start` and
       :py:meth:`~imprint.core.tags.TagDescriptor.end` methods of the
       tag descriptor. It is not one of the XML library immutable
       mappings.

    .. py:attribute:: descriptor

       The :py:class:`~imprint.core.tags.TagDescriptor` object for this
       tag. This must always be an actual instance of the class, not a
       delegate object to be wrapped. Defaults to :py:obj:`None`.

    .. py:attribute:: config

       The :ref:`tag-api-configuration-data` dictionary, if the
       :py:attr:`descriptor` calls for one, :py:obj:`None` otherwise (the
       default). If the descriptor has a
       :py:attr:`~imprint.core.tags.TagDescriptor.data_config` attribute
       set but this attribute is :py:obj:`None`, then
       :py:attr:`open_error` must be set to :py:obj:`True`.

    .. py:attribute:: open_error

       Lets the closing tag know that a non-fatal error occurred on
       opening, so the closing tag processor should be ignored. Defaults\
       to :py:obj:`False`.

    .. py:attribute:: warned

       Indicates that a text content warning has already been issued for
       a tag that has a
       :py:attr:`~imprint.core.tags.TagDescriptor.content` flag set to
       :py:obj:`False` when nested text is found. Otherwise remains
       :py:obj:`False`. This attribute can not be set by the user on
       initialization.
    """
    __slots__ = (
        'name', 'attr', 'descriptor', 'config', 'open_error', 'warned',
    )

    def __init__(self, name, attr, descriptor=None, config=None,
                 open_error=False):
        # Assume that unknown tags may have text so that it gets pasted
        # in literally and the tag itself is ignored.
        self.descriptor = TagDescriptor.wrap(descriptor)
        if descriptor is None:
            self.descriptor.content = True
        self.name = name
        self.attr = attr  # Must be passed a copy
        self.config = config
        self.warned = False
        self.open_error = open_error


class TagStack:
    """
    A :py:class:`~collections.deque`\ -based stack that does some basic
    structural checking of the XML.

    .. py:attribute:: stack

       The actual stack :py:class:`~collections.deque`, implemented as
       a read-only property.

    .. py:attribute:: current

       The current node. This is just the rightmost node in the stack,
       or :py:obj:`None` if the stack is empty. Also a read-only
       property.
    """
    def __init__(self):
        self.__dict__['stack'] = deque()

    @property
    def stack(self):
        """
        Ensure that :py:attr:`stack` is read-only.
        """
        return self.__dict__['stack']

    @property
    def current(self):
        """
        Return the last element of :py:attr:`stack` or :py:obj:`None` if
        empty.
        """
        stack = self.stack
        return stack[-1] if stack else None

    def push(self, node):
        """
        Push a node onto the stack.

        The node is expected to be a :py:class:`TagStackNode` object,
        but no actual checking is done.
        """
        self.stack.append(node)

    def pop(self, name):
        """
        Pop a node from the stack.

        Popping from an empty stack raises a :py:exc:`TypeError`.
        If the name of the current XML tag supplied as ``name`` and
        the name of the tag in the stack do not match, a
        :py:exc:`ValueError` is raised.

        Return the popped tag.
        """
        tag = self.stack.pop()
        if tag.name != name:
            self.log(logging.ERROR, 'Closing mismatched </%s> tag '
                     'for opening <%s> tag', name, tag.name)
            raise ValueError(f'Malformed XML: Unclosed <{tag.name}> tag')
        return tag


class DocxParserBase(SAXLoggable):
    """
    Base class that contains common functionality of the XML parsers
    that make up the Imprint :ref:`introduction-layers-engine`.

    This class is only intended to avoid code duplication. It serves
    no-standalone purpose whatsoever.

    The XML structure is encoded in the following attributes:

    .. py:attribute:: tag_stack

       A stack with special methods for entering a tag, exiting a tag,
       etc, with some structural validation. The current tag is always
       available via the ``current`` property. Each tag is pushed as an
       object containing the tag name, its (edited) attributes, whether
       or not it expects content and nested tags, and a flag indicating
       whether or not a warning has been raised for unexpected text if
       not. If the tag gets a data configuration, that will be
       referenced as well.
    """
    def __init__(self):
        self.tag_stack = TagStack()

    def check_attributes(self, tag, attr, descriptor=None):
        """
        Validate attributes against the optional and required
        specifications and convert them from a
        :py:class:`xml.sax.xmlreader.Attributes` to a plain
        :py:class:`dict`.

        The ``role`` attribute gets special handling: unless it is
        mentioned explicitly, it is always considered to be
        quasi-optional. It will appear in the output only if it appears
        in the input. ``role`` should never be a required attribute,
        although there is nothing preventing custom tags from setting it
        as such.

        Parameters
        ----------
        tag : str
            The name of the tag.
        attr : xml.sax.xmlreader.Attributes
            Limited mapping containing the actual defined attributes of
            the tag.
        descriptor : 
            Any object passed in will be wrapped in a
            :py:class:`~imprint.core.tags.TagDescriptor`.

        Return
        ------
        asdict : dict
            The attributes of the tag, with all required items, and
            missing optional items filled in with defaults.
        descriptor : ~imprint.core.tags.TagDescriptor
            The input descriptor wrapped in an instance of
            :py:class:`TagDescriptor`. Existing references are passed
            through.
        """
        asdict = {}
        extra_keys = attr.keys()
        descriptor = TagDescriptor.wrap(descriptor)

        for name in descriptor.required:
            if name in attr:
                extra_keys.remove(name)
                asdict[name] = attr[name]
            else:
                msg = 'Missing required "%s" attribute from <%s> tag'
                args = (name, tag)
                msg, args = self.locate(msg, *args)
                raise ValueError(msg % args)

        for name, default in descriptor.optional.items():
            if name in attr:
                extra_keys.remove(name)
                asdict[name] = attr[name]
            else:
                self.log(logging.TRACE, 'Missing optional "%s" attribute '
                         'from <%s> tag', name, tag)
                asdict[name] = default

        # This gets special handling
        if 'role' in attr:
            asdict['role'] = attr['role']
            extra_keys.remove('role')
            if 'role' in tag_registry:
                parent = TagDescriptor.wrap(tag_registry['role'])
                reference = parent.reference
                if reference is not None:
                    for name in reference.identifiers:
                        if name in extra_keys:
                            extra_keys.remove(name)
                            asdict[name] = attr[name]
                        elif name not in asdict:
                            if name in parent.required:
                                msg = ('Missing required "%s" attribute from '
                                       '<%s role="%s"> tag')
                                args = (name, tag, attr['role'])
                                msg, args = self.locate(msg, *args)
                                raise ValueError(msg % args)
                            else:
                                asdict[name] = parent.optional[name]

        if extra_keys:
            self.log(logging.WARNING, '<%s> tag contains unknown '
                     'attributes %s', tag, extra_keys)

        return asdict, descriptor

    def set_document_locator(self, locator, level=logging.DEBUG):
        """
        Set the locator and log it with ``DEBUG`` level.
        """
        super().set_document_locator(locator, level=level)


class RootTag(TagDescriptor):
    """
    Implement the :ref:`xml-spec-root` tag, regardless of its name.

    The root tag is special because any spurious text found within it
    gets stashed in a special paragraph.
    """
    def __init__(self):
        """
        Set up the root tag to accept everything.
        """
        self.__dict__.update(
            tags=True,
            content=False,
            required=(),
            optional={},
            data_config=None,
            reference=None,
        )


tag_registry[root_tag] = RootTag()


class ReferenceProcessor(DocxParserBase):
    """
    The SAX parser that is responsible for pre-computing all the relevant
    references found within the XML template.

    Relevant references are any :term:`referenceable` tags. This
    processor maintains its own reference counter based on the occurence
    of :ref:`xml-spec-tags-figure`, :ref:`xml-spec-tags-table` and other
    tags within :ref:`xml-spec-tags-par` tags with *Heading* styles.
    """
    def __init__(self, heading_depth):
        """
        Initialize the parser and the maps it computes.
        """
        super().__init__()
        self.state = ReferenceState(tag_registry, self.log, heading_depth)

    def startElement(self, name, attr):
        """
        Check for referencable tags, either through the tag itself or
        through the :ref:`xml-spec-attributes-role` attribute.

        If the tag is referenceable, the
        :py:meth:`~imprint.core.tags.ReferenceDescriptor.start` method of
        the :py:class:`~imprint.core.tags.ReferenceDescriptor` is run.

        A new node is added to the stack, with the
        :py:class:`~imprint.core.tags.ReferenceDescriptor` set as its
        :py:attr:`~TagStackNode.config` attribute.
        """
        descriptor = tag_registry.get(name, None)
        attr, descriptor = self.check_attributes(name, attr, descriptor)

        if descriptor.reference is not None or 'role' in attr:
            # Role always overrides actual tag
            if 'role' in attr:
                role = attr['role']
                if role not in tag_registry:
                    raise ValueError(f'Invalid role {role!r}: no such tag')
                reference = TagDescriptor.wrap(tag_registry[role]).reference
                if reference is None:
                    raise ValueError(f'Invalid role {role!r}: '
                                     'not referenceable')
            else:
                role = None
                reference = descriptor.reference
            try:
                open_error = not reference.start(self.state, name, role, attr)
            except:
                self.log(logging.ERROR, 'Fatal error in start of reference '
                         'target <%s>', name)
                raise
        else:
            reference = None
            open_error = True

        tag = TagStackNode(name, attr, descriptor, config=reference,
                            open_error=open_error)
        self.tag_stack.push(tag)

    def endElement(self, name):
        """
        Run the :py:meth:`~imprint.core.tags.ReferenceDescriptor.end`
        method of the :py:class:`~imprint.core.tags.ReferenceDescriptor`
        for the tag, if any.

        Also perform a rudimentary structural check on the XML when
        popping the tag stack.
        """
        tag = self.tag_stack.pop(name)
        if tag.open_error:
            self.log(logging.DEBUG,
                     'Ignoring closing </%s> tag: not a reference', name)
            return

        try:
            tag.config.end(self.state, name, tag.attr.get('role'), tag.attr)
        except:
            self.log(logging.ERROR, 'Fatal error in end of reference '
                     'target </%s>', name, exc_info=True)
            raise

    def characters(self, content):
        """
        Record or discard the raw text in a tag, depending on whether
        the :py:class:`~imprint.core.tags.ReferenceDescriptor` of the
        currently open tag wants it or not.
        """
        if 'content' in self.state:
            self.state.content.write(content)
            verb = 'Acquired'
        else:
            verb = 'Ignoring'
        self.log(logging.TRACE, '%s content "%s"', verb, content)


class TemplateProcessor(DocxParserBase):
    """
    A parser to handle the entire document structure with the assumption
    that a reference mapping has already been made.

    It processes all registered tags, generates all the content,
    replaces all necessary components such as keywords, strings and
    references.

    Much of the processing is handled by the built-in
    :py:class:`~imprint.core.tags.TagDescriptor`\ s and the
    :py:class:`~imprint.core.state.EngineState`. The parser itself
    performs sanity checking of the XML structure based on the
    requirements specified in the descriptors. In addition to checking
    attributes, content and nested tags, it performs a simplistic form
    of XML validation.

    The engine state does not get direct access to the data
    configuration like it does to the `keywords`. The data configuration
    is maintained directly by this class:

    .. py:attribute:: data_config

       A :py:class:`dict` containing all of the data configuration
       objects (dictionaries) loaded from the appropriate module if
       `keywords` contains a ``'data_config'`` key providing the
       module file name, and :py:obj:`None` otherwise. Only
       document setups that actually use data configuration need to
       provide a configuration module.
    """
    # This parser's methods are broken into thematically grouped sections

    #
    # Startup
    #

    def __init__(self, keywords, doc, references):
        """
        Initialize the parser, and set up an
        :class:`~imprint.core.state.EngineState` for communication.
        """
        super().__init__()

        if 'data_config' in keywords:
            self.data_config = module_as_dict(keywords['data_config'])
        else:
            self.data_config = None

        self.logger.debug("Initialized for %s", doc)

        self.state = EngineState(doc=doc,
                                 keywords=keywords,
                                 references=references,
                                 log=self.log)
        self.state.new_content(False)

        # Trim the document
        if len(doc.tables) == 0 and len(doc.paragraphs) == 1 and \
                is_paragraph_empty(doc.paragraphs[0]):
            delete_paragraph(doc.paragraphs[0])


    #
    # Internal special-case handlers
    #

    def _handle_os_error(self, exc, tag, id=None):
        """
        Handle :py:exc:`FileNotFoundError` and :py:exc:`PermissionError`
        that occur during tag processing in handlers in a non-fatal way.

        These errors are semi-expected so they get logged, but do not
        cause a fatal crash of the program.
        """
        if isinstance(exc, FileNotFoundError):
            op = 'find'
        elif isinstance(exc, PermissionError):
            op = 'access'
        else:
            raise

        if id is None:
            self.log(logging.ERROR, 'Unable to %s dataset "%s" '
                     'in for %s tag', op, exc.filename, tag)
        else:
            self.log(logging.ERROR, 'Unable to %s dataset "%s" '
                     'in handler for %s "%s"', op, exc.filename, tag, id)
        self.log(logging.TRACE, 'Stack Trace:', exc_info=True)

    def _handle_known_error(self, exc, tag, id=None):
        """
        Handle :py:exc:`~imprint.core.KnownError` that occurs during tag
        processing in handlers in a non-fatal way.

        These errors are semi-expected so they get logged, but do not
        cause a fatal crash of the program.
        """
        if id is None:
            self.log(logging.ERROR, 'Non-fatal error in tag %s: %s',
                     tag, str(exc))
        else:
            self.log(logging.ERROR, 'Non-fatal error in tag %s "%s": %s',
                     tag, id, str(exc))
        self.log(logging.TRACE, 'Caused by:', exc_info=True)

    def _insert_alt_text(self, tag, id, reason):
        """
        Insert a run with alt-text into the current state.

        The logged error will contain the reason for the failure to
        generate content.
        """
        # Missing required configuration
        self.log(logging.ERROR, 'Replacing opening %s '
                 '"%s" with alt-text: %s', tag, id, reason)
        with self.state.temp_run(style=defaults.alt_run_style,
                                 pstyle=defaults.alt_paragraph_style):
            self.state.run.text = f'{{ Insert {tag} [{id}] here }}'

    #
    # Actual processing methods
    #

    def startElement(self, name, attr):
        """
        SAX method to process all open tags.
        """
        # Check if nested tags are allowed at all first
        tag = self.tag_stack.current
        if tag and not tag.descriptor.tags:
            msg = 'Nesting tags in <%s> is forbidden: found <%s>'
            args = tag.name, name
            msg, args = self.locate(msg, *args)
            self.log(logging.Error, msg, *args)
            raise ValueError(msg % args)

        self.log(logging.TRACE, 'Starting element <%s> with attributes %s',
                 name, attr.items())

        descriptor = config = config_name = None
        try:
            if name in tag_registry:
                descriptor = tag_registry[name]
            else:
                # Handle unregistered tags
                self.log(logging.WARNING, 'Unrecognized tag <%s> '
                         'will be ignored', name)
                raise OpenTagError
            attr, descriptor = self.check_attributes(name, attr, descriptor)
            start_args = [self.state, name, attr]
            if descriptor.data_config is not None:
                if self.data_config is None:
                    raise ValueError(
                        'No data configuration defined for parser. Please set '
                        'the `data_configutation` key in your master '
                        'configuration file to point to the appropriate data '
                        'configuration file for this document.'
                    )
                # Handle dynamic configurations
                config_name = attr[descriptor.data_config]
                if config_name in self.data_config:
                    config = self.data_config[config_name]
                    start_args.append(config)
                    self.log(
                        logging.DEBUG, 'Configuration for %s %r:\n%s',
                        name, config_name, pprint.pformat(config, indent=4)
                    )
                else:
                    self._insert_alt_text(name, config_name, 'missing '
                                          'data configuration dictionary')
                    raise OpenTagError

            try:
                descriptor.start(*start_args)
            except KnownError as e:
                self._handle_known_error(e, name, config_name)
                raise OpenTagError
            except OSError as e:
                self._handle_os_error(e, name, config_name)
                raise OpenTagError
            except:
                self.log(logging.ERROR, "Fatal error in start tag for <%s>",
                         name)
                if config_name is not None:
                    self._insert_alt_text(name, config_name,
                                          'Error in opening tag processor')
                raise
        except OpenTagError:
            open_error = True
        else:
            open_error = False

        tag = TagStackNode(name, attr, descriptor, config, open_error)
        self.tag_stack.push(tag)

    def endElement(self, name):
        """
        SAX method to process all closing tags.
        """
        self.log(logging.TRACE, 'Ending element %s', name)
        tag = self.tag_stack.pop(name)
        if tag.open_error:
            self.log(logging.INFO, 'Error in opening tag, '
                     'ignoring closing tag </%s>', name)
            return

        end_args = [self.state, name, tag.attr]
        if tag.config is None:
            config_name = None
        else:
            end_args.append(tag.config)
            config_name = tag.attr[tag.descriptor.data_config]

        try:
            tag.descriptor.end(*end_args)
            err = False
        except KnownError as e:
            self._handle_known_error(e, name, config_name)
            err = True
        except OSError as e:
            self._handle_os_error(e, name, config_name)
            err = True
        except:
            self.log(logging.ERROR, 'Fatal error in end tag for </%s>',
                     name, exc_info=True)
            if config_name is not None:
                self._insert_alt_text(name, config_name,
                                      'Error in closing tag processor')
            err = True
            raise
        finally:
            if err and config_name is not None:
                self._insert_alt_text(name, config_name,
                                      'Error in closing tag processor')

    def characters(self, content):
        """
        SAX method to process all raw text.
        """
        self.log(logging.TRACE, 'Acquired some content: "%s"', content)
        stripped = content.strip()
        tag = self.tag_stack.current
        content_allowed = tag.descriptor.content
        if content_allowed is None and stripped:
            self.log(logging.ERROR, '<%s> tag must be empty: found "%s"',
                     tag.name, stripped)
            raise ValueError('invalid content in <%s> tag' % tag.name)
        if not content_allowed and stripped:
            if not tag.warned:
                self.log(logging.WARNING, 'Unexpected content in <%s>',
                         tag.name)
                tag.warned = True
            if tag.name == root_tag:
                self.log(logging.WARNING, 'Since content is in root, '
                         'a new paragraph will be started')
                self.state.new_run(tag.name, check_in_par=False)
        self.state.content.write(content)

    def endDocument(self):
        """
        SAX method to close the document.
        """
        self.log(logging.TRACE, 'Ending XML document parsing')
        self.state.check_content_tail()
        if 'paragraph' in self.state:
            del self.state.paragraph

    #
    # Things we don't care about (but allow to pass)
    #

    def startDocument(self):
        """
        SAX method to start the document.

        Ignored with a log message.
        """
        self.log(logging.TRACE, "Starting XML document parsing")

    def ignorableWhitespace(self, whitespace):
        """
        SAX method to process ignorable whitespace.

        Ignored with a log message.
        """
        self.log(logging.TRACE, "Encountered ignorable whitespace: \"%s\"", ".".join(whitespace))

    #
    # Things we should never see
    #

    def startPrefixMapping(self, prefix, uri):
        """
        SAX method to begin a prefix mapping.

        This should never happen in an Imprint template.
        """
        self.log(logging.WARNING, "Starting prefix mapping for %s:%s", prefix, uri)

    def endPrefixMapping(self, prefix, uri):
        """
        SAX method to end a prefix mapping.

        This should never happen in an Imprint template.
        """
        self.log(logging.WARNING, "Ending prefix mapping for %s:%s", prefix, uri)

    def startElementNS(self, name, qname, attr):
        """
        SAX method to handle an opening tag with a namespace.

        This should never happen in an Imprint template.
        """
        self.log(logging.WARNING, "Starting namespace element %s (%s) with attributes %s",
                   name, qname, attr.items())

    def endElementNS(self, name, qname):
        """
        SAX method to handle a closing tag with a namespace.

        This should never happen in an Imprint template.
        """
        self.log(logging.WARNING, "Ending namespace element %s (%s)", name, qname)

    def processingInstruction(self, target, data):
        """
        SAX method to handle an XML processing instruction.

        This should never happen in an Imprint template.
        """
        self.log(logging.WARNING, "Encountered processing instruction <%s %s>", target, data)

    def skippedEntity(self, name):
        """
        SAX method to process a skipped XML entity.

        This should never happen in an Imprint template.
        """
        self.log(logging.WARNING, "Encountered skipped entity %s", name)
