"""
    Copyright 2017 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

# based on oslo_config.sphinxext
# http://docs.openstack.org/developer/oslo.config/sphinxext.html

import importlib

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.domains import ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util import logging

from inmanta import data

LOGGER = logging.getLogger(__name__)


def _indent(text, n=2):
    padding = ' ' * n
    return '\n'.join(padding + l for l in text.splitlines())


def _make_anchor_target(group_name, option_name):
    # We need to ensure this is unique across entire documentation
    # http://www.sphinx-doc.org/en/stable/markup/inline.html#ref-role
    target = '%s.%s' % (group_name,
                        option_name.lower())
    return target


class ConfigOptXRefRole(XRefRole):
    "Handles :inmanta.config:option: roles pointing to configuration options."

    def __init__(self):
        super(ConfigOptXRefRole, self).__init__(warn_dangling=True)

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            title = target
        if '.' in target:
            group, opt_name = target.split('.')
        else:
            group = 'DEFAULT'
            opt_name = target
        anchor = opt_name.lower()
        return title, anchor


class EnvironmentSetting(ObjectDescription):
    "Description of a configuration option (.. option)."
    def handle_signature(self, sig, signode):
        """Transform an option description into RST nodes."""
        optname = sig
        LOGGER.info('inmanta.environment-settings setting %s', optname)
        # Insert a node into the output showing the option name
        signode += addnodes.desc_name(optname, optname)
        signode['allnames'] = [optname]
        return optname

    def add_target_and_index(self, firstname, sig, signode):
        cached_options = self.env.domaindata['inmanta.environment-settings']['setting']
        target_name = sig.lower()
        signode['ids'].append(target_name)
        self.state.document.note_explicit_target(signode)
        # Store the location of the option definition for later use in
        # resolving cross-references
        # FIXME: This should take the source namespace into account, too
        cached_options[target_name] = self.env.docname


def _format_setting_help():
    """Generate a series of lines of restructuredtext.

    Format the option help as restructuredtext and return it as a list
    of lines.
    """
    for setting in sorted(data.Environment._settings.values(), key=lambda x: x.name):
        yield f".. inmanta.environment-settings:setting:: {setting.name}"
        yield ""
        if setting.typ != "enum":
            yield _indent(f":Type: {setting.typ}")
        else:
            yield _indent(f":Type: {setting.typ}: {', '.join(setting.allowed_values)}")

        yield _indent(':Default: %s' % setting.default)
        yield ""
        yield _indent(setting.doc)

        yield ""


class ShowEnvironmentSettingsDirective(rst.Directive):

    has_content = True

    def run(self):
        namespaces = [c.strip() for c in self.content if c.strip()]
        for namespace in namespaces:
            importlib.import_module(namespace)

        result = ViewList()
        source_name = '<' + __name__ + '>'
        for line in _format_setting_help():
            result.append(line, source_name)

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)

        return node.children


class EnvironmentSettingsDomain(Domain):
    """inmanta.config domain."""
    name = 'inmanta.environment-settings'
    label = 'inmanta.environment-settings'
    object_types = {
        'setting': ObjType('environment setting', 'setting'),
    }
    directives = {
        'setting': EnvironmentSetting,
    }
    roles = {
        'setting': ConfigOptXRefRole(),
    }
    initial_data = {
        'setting': {},
    }

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        if typ == 'setting':
            try:
                return make_refnode(
                    builder,
                    fromdocname,
                    env.domaindata['inmanta.environment-settings']['setting'][target],
                    target,
                    contnode,
                    target,
                )
            except KeyError:
                # this may get called with an invalid ref by markdown
                pass
        return None


def setup(app):
    app.add_directive('show-environment-settings', ShowEnvironmentSettingsDirective)
    app.add_domain(EnvironmentSettingsDomain)
