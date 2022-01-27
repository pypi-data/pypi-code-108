#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
"""HTML display for Pyxel classes."""

import typing as t

from IPython.core.display import HTML
from jinja2 import Template

from pyxel.pipelines import ModelFunction, ModelGroup


def display_html(obj: t.Union[t.Callable, ModelFunction, ModelGroup]) -> HTML:
    """Display object attributes and their types in a HTML table.

    Parameters
    ----------
    obj: Callable
        Object to display.

    Returns
    -------
    HTML
        HTML object from the rendered template.
    """

    if isinstance(obj, ModelGroup):
        return display_model_group_html(obj)
    elif isinstance(obj, ModelFunction):
        return display_model_html(obj)
    else:

        d = {
            key: [
                type(obj.__dict__[key]).__name__,
                str(obj.__dict__[key]).replace(">", "&gt").replace("<", "&lt"),
            ]
            for key in obj.__dict__.keys()
        }

        template_str = """
        <h4>{{name}}</h4>
        <table>
        <tr>
            <th> ATTRIBUTE </th>
            <th> DTYPE </th>
            <th> VALUE </td>
        </tr>
        {% for key, value in data.items() %}
            <tr>
                <th> {{ key }} </th>
                <td> {{ value[0] }} </td>
                <td> {{ value[1] }} </td>
            </tr>
        {% endfor %}
        </table>"""

        template = Template(template_str)

        return HTML(template.render(data=d, name=obj.__class__.__name__))


def display_model_html(mf: "ModelFunction") -> HTML:
    """Display ModelFunction attributes and their types in a HTML table.

    Parameters
    ----------
    mf: ModelFunction
        Model function.

    Returns
    -------
    HTML
        HTML object from the rendered template.
    """
    d = {
        key: [
            type(mf.__dict__[key]).__name__,
            str(mf.__dict__[key]).replace(">", "&gt").replace("<", "&lt"),
        ]
        for key in mf.__dict__.keys()
    }
    a = {
        key: [
            type(mf._arguments[key]).__name__,
            str(mf._arguments[key]).replace(">", "&gt").replace("<", "&lt"),
        ]
        for key in mf._arguments.keys()
    }

    template_str = """
    <h4>ModelFunction: {{model_name}}</h4>
    <table>
    <tr>
        <th> ATTRIBUTE </th>
        <th> DTYPE </th>
        <th> VALUE </td>
    </tr>
    {% for key, value in data.items() %}
        <tr>
            <th> {{ key }} </th>
            <td> {{ value[0] }} </td>
            <td> {{ value[1] }} </td>
        </tr>
    {% endfor %}
    </table>
    <h5>Arguments</h5>
    <table>
    <tr>
        <th> ATTRIBUTE </th>
        <th> DTYPE </th>
        <th> VALUE </td>
    </tr>
    {% for key, value in arguments.items() %}
        <tr>
            <th> {{ key }} </th>
            <td> {{ value[0] }} </td>
            <td> {{ value[1] }} </td>
        </tr>
    {% endfor %}
    </table>
    """

    template = Template(template_str)

    return HTML(template.render(data=d, arguments=a, model_name=mf._name))


def display_model_group_html(mg: "ModelGroup") -> HTML:
    """Display ModelGroup attributes and their types in a HTML table.

    Parameters
    ----------
    mg: ModelGroup
        Model group.

    Returns
    -------
    HTML
        HTML object from the rendered template.
    """

    d = {
        key: [
            type(mg.__dict__[key]).__name__,
            str(mg.__dict__[key]).replace(">", "&gt").replace("<", "&lt"),
        ]
        for key in mg.__dict__.keys()
    }
    m = {
        model._name: [
            type(model).__name__,
            f"{model!r}".replace(">", "&gt").replace("<", "&lt"),
        ]
        for model in mg.models
    }

    template_str = """
    <h4>ModelGroup: {{model_group_name}}</h4>
    <table>
    <tr>
        <th> ATTRIBUTE </th>
        <th> DTYPE </th>
        <th> VALUE </td>
    </tr>
    {% for key, value in data.items() %}
        <tr>
            <th> {{ key }} </th>
            <td> {{ value[0] }} </td>
            <td> {{ value[1] }} </td>
        </tr>
    {% endfor %}
    </table>
    <h5>Models</h5>
    <table>
    <tr>
        <th> ATTRIBUTE </th>
        <th> DTYPE </th>
        <th> VALUE </td>
    </tr>
    {% for key, value in models.items() %}
        <tr>
            <th> {{ key }} </th>
            <td> {{ value[0] }} </td>
            <td> {{ value[1] }} </td>
        </tr>
    {% endfor %}
    </table>
    """

    template = Template(template_str)

    return HTML(template.render(data=d, models=m, model_group_name=mg._name))
