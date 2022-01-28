"""Finesse Sphinx extension.

This provides the `kat:command`, `kat:element` and `kat:analysis` directives and indices
to provide a means to automatically document and cross-reference KatScript instructions.

Loosely based on https://www.sphinx-doc.org/en/master/development/tutorials/recipe.html
and https://github.com/click-contrib/sphinx-click/blob/master/sphinx_click/ext.py.

Short description of how Sphinx, Docutils and this module works:

Sphinx ultimately relies upon the Python library `docutils` to generate the Finesse
documentation. This provides a way to define the document structure independently from
the target final format. By defining the document in this way, Sphinx (via docutils) can
generate the various output formats (HTML, PDF, etc.) as required. The docutils library
provides most of the low-level elements for building the document such as those that
represent paragraphs, section headers, lists, etc. Sphinx adds some higher order classes
that represent more complex structures such as class definitions, as well as providing
support for generating indices, contents lists, cross-references, etc.

Docutils documents are a tree of "nodes", similar to an HTML document. The node types
that represent various types of textual, structural and decorative elements are defined
in :mod:`docutils.nodes` and :mod:`sphinx.addnodes`.

The `finesse_sphinx` package registers several new Sphinx objects for referencing and
generating documentation for items such as KatScript elements. These are special classes
that interact with Sphinx while the Finesse documentation is being generated to inject
additional content and references and to create additional index entries.

Documentation for building custom Sphinx extensions such as those in this module is
unfortunately very limited. The main reference is the Sphinx source code itself,
particularly the `autodoc` extension, which implements similar behaviours to those of
the extensions here.

Author: Sean Leavey
"""

import abc
from collections import defaultdict
from inspect import getabsfile
from docutils import nodes
from docutils.statemachine import ViewList
from sphinx import addnodes
from sphinx.domains import Domain, Index
from sphinx.roles import XRefRole
from sphinx.util.docutils import SphinxDirective, ReferenceRole
from sphinx.util.nodes import make_refnode, nested_parse_with_titles
from finesse.script.spec import KatSpec

__version__ = "0.9.1"

_SPEC = KatSpec()


def kat_syntax(adapter):
    """Build kat syntax string for `adapter`."""
    return adapter.documenter.syntax(_SPEC, adapter)


class IssueRole(ReferenceRole):
    """Support for referencing issues in the Finesse source repository.

    Based on Sphinx's PEP role.
    """

    def run(self):
        # Add an index entry.
        target_id = "index-%s" % self.env.new_serialno("index")
        entries = [("single", f"Finesse issues; #{self.target}", target_id, "", None)]

        index = addnodes.index(entries=entries)
        target = nodes.target("", "", ids=[target_id])
        self.inliner.document.note_explicit_target(target)

        try:
            refuri = self.build_uri()
            reference = nodes.reference(
                "", "", internal=False, refuri=refuri, classes=["finesse-issue"]
            )
            if self.has_explicit_title:
                reference += nodes.strong(self.title, self.title)
            else:
                title = f"#{self.title}"
                reference += nodes.strong(title, title)
        except ValueError:
            msg = self.inliner.reporter.error(
                f"invalid Finesse issue {self.target}", line=self.lineno
            )
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        return [index, target, reference], []

    def build_uri(self):
        return self.config.finesse_issue_uri % int(self.target)


class SourceRole(ReferenceRole):
    """Support for referencing source code in the Finesse source repository.

    Based on Sphinx's PEP role.
    """

    def run(self):
        # Add an index entry.
        target_id = "index-%s" % self.env.new_serialno("index")
        entries = [
            ("single", f"Finesse source code; {self.target}", target_id, "", None)
        ]

        index = addnodes.index(entries=entries)
        target = nodes.target("", "", ids=[target_id])
        self.inliner.document.note_explicit_target(target)

        try:
            refuri = self.build_uri()
            reference = nodes.reference(
                "", "", internal=False, refuri=refuri, classes=["finesse-source-code"]
            )
            reference += nodes.strong(self.title, self.title)
        except ValueError:
            msg = self.inliner.reporter.error(
                f"invalid Finesse source code path {self.target}", line=self.lineno
            )
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        return [index, target, reference], []

    def build_uri(self):
        if self.target.startswith("/"):
            # This is relative to the project root.
            return self.config.finesse_source_root_uri % self.target.lstrip("/")
        # This is relative to the Finesse package root.
        return self.config.finesse_source_package_uri % self.target


class InstructionDirective(SphinxDirective, metaclass=abc.ABCMeta):
    """A custom Sphinx directive that describes a KatScript instruction."""

    description = "Instruction"
    has_content = True
    required_arguments = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        directive = self.arguments[0]
        try:
            self.adapter = _SPEC.directives[directive]
        except KeyError:
            raise ValueError(
                f"directive {directive} doesn't exist in KatScript language spec"
            )

    def _description_slug(self):
        """Description type, usable as HTML attribute."""
        return nodes.fully_normalize_name(self.description)

    def _alias_slug(self, alias):
        return nodes.make_id(f"kat-{self._description_slug()}-{alias}")

    def _params(self):
        required_params = []
        optional_params = []

        descriptions = self.adapter.documenter.argument_descriptions()
        for param_name, (param_type, param_doc) in descriptions.items():
            param = param_name, param_doc
            if "optional" in param_type:
                optional_params.append(param)
            else:
                required_params.append(param)

        return required_params, optional_params

    def run(self):
        """Generate the nodes that represent this directive.

        This generates the signature line (directive aliases), summary, parameter lists
        and any other content specified in the restructuredText document.
        """
        doc_type = self.adapter.documenter.doc_type

        try:
            source = getabsfile(doc_type)
        except TypeError:
            # This may be a Cythonised target. Use the string name instead.
            source = doc_type.__name__

        kat = self.env.get_domain("kat")

        if ":" not in self.name:
            raise ValueError(
                f"incorrect name format '{self.name}'; must be of the form 'kat:thing'"
            )

        self.domain, self.objtype = self.name.split(":", 1)

        # Create the index target for the instruction, just before the signature in the
        # document.
        index_node = addnodes.index(entries=[])

        node = addnodes.desc()
        node.document = self.state.document
        node["domain"] = self.domain
        node["objtype"] = self.objtype
        node["noindex"] = noindex = "noindex" in self.options
        node["classes"].append(self.domain)
        node["classes"].append(node["objtype"])

        # Create the signature and index entries for each alias.
        signature_node = addnodes.desc_signature("", "", is_multiline=True)
        self.set_source_info(signature_node)
        node += signature_node
        for alias in self.adapter.aliases:
            is_primary = alias == self.adapter.full_name

            # All signatures have anchors due to the signature_node["ids"] line below,
            # but add_permalink shows a "#" next to the signature that users can copy.
            signature_line = addnodes.desc_signature_line("", add_permalink=is_primary)
            signature_line += addnodes.desc_name(text=alias)
            signature_node += signature_line

            # Map index entry.
            if not noindex:
                anchor = self._alias_slug(alias)

                # Register an anchor for this alias.
                signature_node["ids"].append(anchor)

                kat.add_instruction(anchor, self, alias)

                if "noindexentry" not in self.options:
                    # Add an index entry for this alias.
                    index_text = f"{alias} (KatScript {self.description})"
                    entry = ("single", index_text, anchor, "", None)
                    index_node["entries"].append(entry)

        # Create a node to contain this instruction's documentation.
        content_node = addnodes.desc_content()
        self.set_source_info(content_node)
        node += content_node

        ##
        # The summary.
        ##

        summary = self.adapter.documenter.summary()
        if summary is None:
            summary = ""
        # Parse the docstring summary.
        summary_rst = ViewList()
        for line in summary.splitlines():
            summary_rst.append(line, source)
        self.state.nested_parse(summary_rst, 0, content_node)

        # Field list (mapping of entries like "Syntax" to corresponding content).
        fields = nodes.field_list()
        content_node += fields

        ##
        # The syntax.
        ##

        syntax = kat_syntax(self.adapter)
        syntax_code_block = nodes.literal_block("", syntax)
        # syntax_code_block["language"] = "KatScript"  # Doesn't work with variadic args.
        syntax_code_block["classes"].append("kat-instruction-syntax")
        syntax_node = nodes.field()
        syntax_node += nodes.field_name("", "Syntax")
        syntax_node += nodes.field_body("", syntax_code_block)
        fields += syntax_node

        ##
        # The parameters.
        ##

        required_params, optional_params = self._params()

        def param_field(desc, params):
            params_node = nodes.field()
            params_node += nodes.field_name("", desc)
            field_body = nodes.field_body()
            params_node += field_body

            for pnames, description in params:
                # Make the parameter(s) appear as literal text.
                param_names = ""
                for i, pname in enumerate(pnames.split(",")):
                    if i > 0:
                        param_names += ", "
                    param_names += f"``{pname.strip()}``"

                description = f"{param_names}: {description}"

                # Parse the description rsT.
                param_rst = ViewList()
                for line in description.strip().splitlines():
                    param_rst.append(line, source)
                self.state.nested_parse(param_rst, 0, field_body)

            return params_node

        if required_params:
            fields += param_field("Required", required_params)
        if optional_params:
            fields += param_field("Optional", optional_params)

        ##
        # Any extra rST specified in the rST file.
        ##

        content = ViewList()
        for line in self.content:
            content.append(line, source)
        content.append("", source)
        nested_parse_with_titles(self.state, content, content_node)

        return [index_node, node]


class CommandDirective(InstructionDirective):
    """A custom directive that describes a kat script command."""

    description = "Command"


class ElementDirective(InstructionDirective):
    """A custom directive that describes a kat script element."""

    description = "Element"


class AnalysisDirective(InstructionDirective):
    """A custom directive that describes a kat script analysis."""

    description = "Analysis"


class KatIndex(Index, metaclass=abc.ABCMeta):
    """A custom index that creates an instruction matrix."""

    index_type = None

    def generate(self, docnames=None):
        content = defaultdict(list)

        # Sort the list of instructions in alphabetical order.
        instructions = self.domain.get_objects()
        instructions = sorted(instructions, key=lambda instruction: instruction[0])

        # Generate the expected output, shown below, from the above using the first
        # letter of the recipe as a key to group thing.
        #
        # name, subtype, docname, anchor, extra, qualifier, description
        for name, dispname, typ, docname, anchor, _ in instructions:
            if typ != self.index_type:
                continue

            display_name = self.format_display_name(dispname)
            description = typ

            # The key is the index (in this case, the first character).
            content[display_name[0].lower()].append(
                (display_name, 0, docname, anchor, docname, "", description)
            )

        # Convert the dict to the sorted list of tuples expected.
        content = sorted(content.items())

        return content, True

    def format_display_name(self, name):
        return name


class CommandIndex(KatIndex):
    """A custom index that creates a command matrix."""

    name = "commandindex"
    localname = "Command Index"
    shortname = "Command"
    index_type = "Command"


class ElementIndex(KatIndex):
    """A custom index that creates an element matrix."""

    name = "elementindex"
    localname = "Element Index"
    shortname = "Element"
    index_type = "Element"


class AnalysisIndex(KatIndex):
    """A custom index that creates an analysis matrix."""

    name = "analysisindex"
    localname = "Analysis Index"
    shortname = "Analysis"
    index_type = "Analysis"


class KatDomain(Domain):
    name = "kat"
    label = "Kat Domain"
    roles = {
        "command": XRefRole(),
        "element": XRefRole(),
        "analysis": XRefRole(),
    }
    directives = {
        "command": CommandDirective,
        "element": ElementDirective,
        "analysis": AnalysisDirective,
    }
    indices = {
        CommandIndex,
        ElementIndex,
        AnalysisIndex,
    }
    initial_data = {
        "instructions": [],  # Object list.
    }

    def get_full_qualified_name(self, node):
        return "{}.{}".format("instruction", node.arguments[0])

    def get_objects(self):
        yield from self.data["instructions"]

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        # Match the specified reference to an alias of the available kat script
        # directives.
        if typ == "command":
            match = [
                (docname, anchor)
                for name, sig, otyp, docname, anchor, prio in self.get_objects()
                if (otyp == "Command" and target in _SPEC.commands[sig].aliases)
            ]
        elif typ == "element":
            match = [
                (docname, anchor)
                for name, sig, otyp, docname, anchor, prio in self.get_objects()
                if (otyp == "Element" and target in _SPEC.elements[sig].aliases)
            ]
        elif typ == "analysis":
            match = [
                (docname, anchor)
                for name, sig, otyp, docname, anchor, prio in self.get_objects()
                if (otyp == "Analysis" and target in _SPEC.analyses[sig].aliases)
            ]
        else:
            match = []

        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]

            return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
        else:
            print(f"Did not find kat script instruction for xref '{target}'")
            return None

    def add_instruction(self, anchor, instruction, signature):
        """Add a new instruction to the domain."""
        name = "{}.{}".format("instruction", signature)

        # name, dispname, type, docname, anchor, priority
        self.data["instructions"].append(
            (name, signature, instruction.description, self.env.docname, anchor, 0)
        )

    def merge_domaindata(self, docnames, otherdata):
        self.data["instructions"].extend(otherdata["instructions"])


def setup(app):
    app.add_config_value(
        "finesse_issue_uri", "https://git.ligo.org/finesse/finesse3/-/issues/%d", "html"
    )
    app.add_config_value(
        "finesse_source_root_uri",
        "https://git.ligo.org/finesse/finesse3/-/tree/master/%s",
        "html",
    )
    app.add_config_value(
        "finesse_source_package_uri",
        "https://git.ligo.org/finesse/finesse3/-/tree/master/src/finesse/%s",
        "html",
    )
    app.add_role("issue", IssueRole())
    app.add_role("source", SourceRole())
    app.add_domain(KatDomain)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
