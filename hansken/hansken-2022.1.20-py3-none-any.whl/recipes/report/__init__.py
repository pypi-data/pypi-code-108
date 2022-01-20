# encoding=utf-8

from io import open

from logbook import Logger


log = Logger(__name__)

try:
    from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader
except ImportError as e:
    raise ImportError('jinja2 is not available; install hansken.py with the "report" or "all" '
                      'extras (e.g. pip install hansken[report]), or install jinja2 manually') from e


try:
    from weasyprint import HTML
except (ImportError, OSError) as e:
    log.warning('failed to import weasyprint, PDF rendering will not be available', e)

    def missing_lib(*args, **kwargs):
        raise ImportError('weasyprint is not available; install hansken.py with the "report" or "all" '
                          'extras (e.g. pip install hansken[report]), or install weasyprint manually')

    HTML = missing_lib


# load templates from the included template directory by default
default_loader = PackageLoader(__name__)


class HanskenTemplateEnvironment(Environment):
    """
    An extension of jinja2's `Environment` type for the sole purpose of
    overriding `__repr__` to show a more friendly default argument for
    templating calls below.
    """
    def __repr__(self):
        return '<hansken.py default environment>'


default_environment = HanskenTemplateEnvironment(loader=default_loader, autoescape=True)


def environment_with(searchpath=None, loader=None, **kwargs):
    """
    Create an `Environment` loaded with ``hansken.py`` 's provided templates,
    while adding the provided search path or loader as a template source that
    precedes the provided templates. The resulting `Environment` is set to
    auto-escaping unless explicitly set to ``False`` in *kwargs*.

    :param searchpath: `str` or sequence `str` of paths containing templates
    :param loader: a Jinja2 template loader to use in conjunction with
        ``hansken.py`` 's `.default_loader`
    :param kwargs: arguments passed to `Environment`, see `the Jinja2
        documentation <http://jinja.pocoo.org/docs/2.10/>`_
    :return: an `Environment`, loading templates from both *searchpath* and
        `.template_path`
    """
    if (searchpath and loader) or not (searchpath or loader):
        # we'll require exactly one of the options
        raise ValueError('provide either searchpath or loader')

    if not loader:
        # only searchpath was provided, create a loader from it
        loader = FileSystemLoader(searchpath)

    # default auto-escaping to True
    kwargs.setdefault('autoescape', True)

    return HanskenTemplateEnvironment(loader=ChoiceLoader((loader, default_loader)), **kwargs)


def render_template(template_name, environment=default_environment, **kwargs):
    """
    Render a named template.

    :param template_name: the name of the template to be rendered (e.g.
        ``'hansken/table.html'``)
    :param environment: the `Environment` to be used, defaults to the template
        environment defined by ``hansken.py``
    :param kwargs: named arguments to pass to the template
    :return: a `str` containing the rendered template
    """
    template = environment.get_template(template_name)
    return template.render(**kwargs)


def render_string(string, environment=default_environment, **kwargs):
    """
    Render an anonymous template, provided as a `str`.

    :param string: the template content to be rendered
    :param environment: the `Environment` to be used, defaults to the template
        environment defined by ``hansken.py``
    :param kwargs: named arguments to pass to the template
    :return: a `str` containing the rendered template
    """
    template = environment.from_string(string)
    return template.render(**kwargs)


def to_html_table(output, traces, fields):
    """
    Render *traces* into an HTML table and save to *output*.

    :param output: name of the file to write to
    :param traces: collection of `.Trace` objects to render (typically a
        `.SearchResult`)
    :param fields: fields to retrieve values for, a sequence of property names
        (`str`)
    """
    with open(output, 'wt') as output:
        output.write(render_template('hansken/table.html', traces=traces, fields=fields))


def to_pdf(output, content, base_url='.', **pdf_options):
    """
    Save HTML *content* as PDF to *output*.

    :param output: name of the file to write to
    :param content: HTML content to write to PDF
    :param base_url: base url for resolving linked resources in the template
        (typically only useful when providing custom style sheets, see
        WeasyPrint documentation)
    :param pdf_options: keyword arguments passed verbatim to `HTML.write_pdf`
        (see WeasyPrint documentation)
    """
    HTML(string=content, base_url=base_url).write_pdf(output, **pdf_options)


def to_pdf_table(output, traces, fields, base_url='.', **pdf_options):
    """
    Render *traces* into a table and save as PDF to *output*.

    :param output: name of the file to write to
    :param traces: collection of `.Trace` objects to render (typically a
        `.SearchResult`)
    :param fields: fields to retrieve values for, a sequence of property names
        (`str`)
    :param base_url: base url for resolving linked resources in the template
        (typically only useful when providing custom style sheets, see
        WeasyPrint documentation)
    :param pdf_options: keyword arguments passed verbatim to `HTML.write_pdf`
        (see WeasyPrint documentation)
    """
    content = render_template('hansken/table.html', traces=traces, fields=fields)
    to_pdf(output, content, base_url=base_url, **pdf_options)
