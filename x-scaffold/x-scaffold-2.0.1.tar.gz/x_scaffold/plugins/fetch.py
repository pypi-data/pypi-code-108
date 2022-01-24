import os
import pathlib

from ..context import ScaffoldContext

from ..rendering import render, render_options, render_token_file, render_tokens
from ..steps import ScaffoldStep
from ..runtime import ScaffoldRuntime
from ..plugin import ScaffoldPluginContext

from fnmatch import fnmatch


def init(context: ScaffoldPluginContext):
    context.add_step('fetch', FetchStep())


def is_match(path, patterns):
    for pattern in patterns:
        if fnmatch(path, pattern):
            return True
    return False


def render_file(path, context):
    """Used to render a Jinja template."""

    template_dir, template_name = os.path.split(path)
    return render(template_name, context, template_dir)


class FetchStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        opts = render_options(step, context)
        pkg_dir = context['__package']['path']
        full_pkg_dir = os.path.realpath(pkg_dir)
        
        target = opts.get('target', '.')
        target_base = os.path.realpath(context.get('__target', '.'))
        full_target = os.path.realpath(os.path.join(target_base, target))
        source = opts.get('source', '**/*')

        templates = opts.get('templates', [])
        exclude = opts.get('exclude', []) + ['.git', '.git/*']

        paths = pathlib.Path(full_pkg_dir).rglob(source)

        for p_obj in paths:
            p = str(p_obj)
            tfile = p[len(full_pkg_dir)+1:]
            t = os.path.join(full_target, tfile)
            tbase, tname = os.path.split(t)
            if is_match(tfile, exclude):
                continue
            if not os.path.exists(tbase):
                os.makedirs(tbase)

            if p_obj.is_file():
                template = get_template(tfile, templates)
                if template:
                    if 'tokens' in template:
                        content = render_token_file(p, template['tokens'])
                    else:
                        content = render_file(p, context)
                    with open(t, 'w') as fhd:
                        fhd.write(content)
                else:
                    with open(p, 'r') as fhd:
                        with open(t, 'w') as fhd2:
                            fhd2.write(fhd.read())

def get_template(path, templates):
    for template in templates:
        if fnmatch(path, template['path']):
            return template
    return None
