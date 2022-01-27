# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 13:10:57 2022

@author: Alexander Southan
"""

from sympy import latex
from latex2mathml import converter
from docx import Document
from lxml import etree


def math_to_word(math_expression, equals=None, mode='SymPy', word_file=None,
                 replace={}):
    """
    Transform a sympy input into a format suitable for MS Word documents.

    This is heavily inspired by: 
        https://github.com/python-openxml/python-docx/issues/320

    Parameters
    ----------
    math_expression : SymPy object or LaTeX math mode string
        Either a SymPy object suitable to pass to SymPy´s latex method or a
        LaTeX math mode string, as defined by mode.
    equals : same type as math_expression, optional
        If given, an equation is returned that containes math_expression on the
        left side and equals on the right side.
    mode : string, optional
        Defines the type of input that is given to the function. Can either be
        'SymPy', so that a SymPy object is expected, or 'LaTeX', so that a
        LaTeX math mode string is expected.
    word_file : string, optional
        The path including the file name to save the equation to.
    replace : dict, optional
        A dictionary with keys that are sercged in the string on the latex
        level and replaced by the corresponding values. This allows to use more
        complex symbol names. The default is {}.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    modes = ['SymPy', 'LaTeX']
    if mode == 'SymPy':
        # Convert sympy input to LaTeX string
        latex_input = latex(math_expression)
        if equals is None:
            equals_input = ''
        else:
            equals_input = '=' + latex(equals)
    elif mode == 'LaTeX':
        latex_input = math_expression
        if equals is None:
            equals_input = ''
        else:
            equals_input = '=' + equals_input
    else:
        raise ValueError(
            'Invalid value for mode. Allowed values are in {}, but {} was'
            'given.'.format(modes, mode))

    latex_input = latex_input + equals_input

    # Replace symbol names on LaTeX level for more complex symbol names
    for old_str, new_str in replace.items():
        latex_input = latex_input.replace(old_str, new_str)

    # Convert LaTeX string to MathML that can be written to Word file
    mathml = converter.convert(latex_input)
    tree = etree.fromstring(mathml)
    xslt = etree.parse(
        'C:/Program Files (x86)/Microsoft Office/Office16/MML2OMML.XSL')
    transform = etree.XSLT(xslt)
    new_dom = transform(tree)

    if word_file is not None:
        doc = Document()
        p = doc.add_paragraph()
        p._element.append(new_dom.getroot())
        doc.save(word_file)

    return new_dom.getroot()
