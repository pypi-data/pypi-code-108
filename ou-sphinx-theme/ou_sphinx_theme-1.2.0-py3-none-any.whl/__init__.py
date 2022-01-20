import json
import sphinx
import sphinx.builders.html

from base64 import b64encode
from docutils.nodes import bullet_list, list_item, paragraph, reference
from os import path
from sphinx.environment.adapters.toctree import TocTree
from sphinx.util.osutil import ensuredir

from .ext import a11y, activity, iframe, youtube


def get_nav_entry(parent):
    """Convert a toctree list item into a nav-entry dict."""
    if isinstance(parent, list_item):
        reference = parent.children[0].children[0]
    elif isinstance(parent, paragraph):
        reference = parent.children[0]
    expanded = ('iscurrent' in parent.attributes and parent.attributes['iscurrent'])
    current = ('iscurrent' in reference.attributes and reference.attributes['iscurrent'])
    return {'title': reference.astext(),
            'url': reference.attributes['refuri'],
            'current': current,
            'expanded': expanded,
            'children': []}


def get_block_nav(self, pagename):
    """Get the navigation entries for the top-level TOC entries."""
    toctree = TocTree(self.env).get_toctree_for(pagename, self, collapse=False, maxdepth=-1)
    return [get_nav_entry(item) for item in toctree.children[0].children if isinstance(item, list_item)]


def get_prev_next_nav(prev_next):
    """Return either the previous or next nav entry."""
    if prev_next:
        return {'title': prev_next['title'],
                'url': prev_next['link']}
    else:
        return None


def build_nav_tree(self, node):
    """Recursively build a navigation tree."""
    entry = get_nav_entry(node)
    if node.children:
        for child in node.children:
            if isinstance(child, bullet_list):
                for item in child.children:
                    entry['children'].append(build_nav_tree(self, item))
    return entry


def get_within_block_nav(self, pagename):
    """Build the within-the-block navigation."""
    toctree = TocTree(self.env).get_toctree_for(pagename, self, collapse=False, maxdepth=-1)
    for top_level in toctree.children[0].children:
        if isinstance(top_level, list_item):
            entry = get_nav_entry(top_level)
            if entry['current'] or entry['expanded']:
                return build_nav_tree(self, top_level)
    return None


def find_node(self, node, pagename):
    """Find the node for the ``pagename``."""
    if isinstance(node, list_item):
        entry = get_nav_entry(node)
        if self.env.relfn2path(entry['url'], pagename)[0].split('/')[-1] == '':
            return node
        for child in node.children:
            tmp = find_node(self, child, pagename)
            if tmp:
                return tmp
    elif isinstance(node, bullet_list):
        for child in node.children:
            tmp = find_node(self, child, pagename)
            if tmp:
                return tmp
    elif isinstance(node, paragraph):
        entry = get_nav_entry(node)
        if entry['url'] == '':
            return node
    return None


def resolve_pagename(pagename):
    """Resolve a pagename, removing all ``..``."""
    resolved = []
    for part in pagename.split('/'):
        if part == '..':
            resolved.pop()
        else:
            resolved.append(part)
    return '/'.join(resolved)


def get_ancestor_pagenames(self, pagename):
    """Get a list of all ancestor pagenames."""
    toctree = TocTree(self.env).get_toctree_for(pagename, self, collapse=False, maxdepth=-1)
    for top_level in toctree.children[0].children:
        tmp = find_node(self, top_level, pagename)
        if tmp:
            result = []
            if isinstance(tmp, list_item):
                parent = tmp.parent.parent
            elif isinstance(tmp, paragraph):
                parent = tmp.parent
            while parent:
                if isinstance(parent, list_item):
                    parent_pagename = self.env.relfn2path(get_nav_entry(parent)['url'], pagename)[0]
                    if parent_pagename.endswith('.html'):
                        parent_pagename = parent_pagename[:-5]
                    result.append(resolve_pagename(parent_pagename))
                if parent.parent:
                    parent = parent.parent.parent
                else:
                    parent = None
            result.reverse()
            return result
    return []


def update_page_context(self, pagename, templatename, context, event_arg):
    """Update the page context with the data needed for the OU Sphinx Theme."""
    if 'body' in context:
        metadata = {}
        for ancestor in get_ancestor_pagenames(self, pagename):
            if ancestor in self.env.metadata:
                metadata.update(self.env.metadata[ancestor])
        if 'meta' in context and context['meta']:
            metadata.update(context['meta'])
        data = {
            'metadata': metadata,
            'project': {
                'name': context['project'],
                'release': context['release'],
            },
            'urls': {
                'root': context['pathto'](context['master_doc']),
                'static': context['pathto']('_static', 1),
            },
            'tutorial': {
                'blocks': [{'title': 'Home', 'url': context['pathto'](context['master_doc'])}] + get_block_nav(self, pagename),
                'body': context['body'],
                'next': get_prev_next_nav(context['next']),
                'prev': get_prev_next_nav(context['prev']),
                'title': context['title'],
                'withinBlockNav': get_within_block_nav(self, pagename),
            }
        }
        context['json_blob'] = b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        outfilename = self.get_outfilename(pagename)
        if outfilename.endswith('.html'):
            outfilename = outfilename.replace('.html', '.json')
            ensuredir(path.dirname(outfilename))
            with open(outfilename, 'w') as out_f:
                json.dump(data, out_f)


def setup(app):
    """Setup the OU Sphinx theme and extensions."""
    app.add_html_theme('openuniversity', path.abspath(path.dirname(__file__)))
    sphinx.builders.html.StandaloneHTMLBuilder.update_page_context = update_page_context
    a11y.setup(app)
    activity.setup(app)
    iframe.setup(app)
    youtube.setup(app)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
