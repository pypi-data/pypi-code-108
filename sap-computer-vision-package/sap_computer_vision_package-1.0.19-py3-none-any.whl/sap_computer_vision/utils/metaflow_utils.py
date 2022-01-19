"""This module contain small helper functions used by the aif pipelines."""
import textwrap

from metaflow import FlowSpec


def add_parameters_help_to_doc_string(flow: 'FlowSpec'):
    """Utility function to append parameters to
    metaflow.FlowSpec doc string.

    Patameter
    ---------
    flow: metaflow.FlowSpec
        The flow of which the DocString should be extended.
    """
    doc_str = []
    for name, par in flow._get_parameters(flow):
        par_str = [par.name, '--------']
        if 'default' in par.kwargs:
            par_str.append(f'default={par.kwargs["default"]}')
        if 'type' in par.kwargs:
            try:
                type_str = par.kwargs["type"].__name__
            except:
                type_str = str(par.kwargs["type"])
            par_str.append(f'type={type_str}')
        help_str = par.kwargs.get('help', '')
        if len(help_str) > 0:
            help_str = textwrap.indent('\n'.join(textwrap.wrap(help_str)), '    ')
        par_str.append(help_str)
        doc_str.append('\n'.join(par_str))
    flow.__doc__ += '\n' + '\n\n'.join(doc_str)
