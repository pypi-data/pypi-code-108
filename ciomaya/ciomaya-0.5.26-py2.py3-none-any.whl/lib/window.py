# -*- coding: utf-8 -*-
"""
Submit.
"""
import json

import traceback

import pymel.core as pm
from ciocore import config


try:
    import urlparse as parse
except ImportError:
    from urllib import parse


def about_conductor():
    version = pm.moduleInfo(version=True, moduleName="conductor")
    definition = pm.moduleInfo(definition=True, moduleName="conductor")
    path = pm.moduleInfo(path=True, moduleName="conductor")

    result = """
Conductor for Maya

        Module version: {}
   Module install path: {}
Module definition file: {}

LICENSE INFORMATION

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Copyright © 2020, Conductor Technologies.
    """.format(
        version, path, definition
    )

    return result


def layout_form(form, text, main_layout, *buttons):
    form.attachForm(text, "left", 2)
    form.attachForm(text, "right", 2)
    form.attachForm(text, "top", 2)
    form.attachNone(text, "bottom")

    form.attachForm(main_layout, "left", 2)
    form.attachForm(main_layout, "right", 2)
    form.attachControl(main_layout, "top", 2, text)
    form.attachControl(main_layout, "bottom", 2, buttons[0])

    form.attachForm(buttons[0], "left", 2)
    form.attachNone(buttons[0], "top")
    form.attachForm(buttons[0], "bottom", 2)

    if len(buttons) == 1:
        form.attachForm(buttons[0], "right", 2)
    else:  # 2
        form.attachPosition(buttons[0], "right", 2, 50)

        form.attachPosition(buttons[1], "left", 2, 50)
        form.attachForm(buttons[1], "right", 2)
        form.attachNone(buttons[1], "top")
        form.attachForm(buttons[1], "bottom", 2)


def show_as_json(data, **kw):
    title = kw.get("title", "Json Window")
    indent = kw.get("indent", 2)
    sort_keys = kw.get("sort_keys", True)
    result_json = json.dumps(data, indent=indent, sort_keys=sort_keys)
    pm.window(width=600, height=800, title=title)
    pm.frameLayout(cll=False, lv=False)
    pm.scrollField(text=result_json, editable=False, wordWrap=False)
    pm.showWindow()

def _dismiss():
    pm.layoutDialog(dismiss="abort")

def _okay():
    pm.layoutDialog(dismiss="okay")

def _get_numeric_code(response):
    code = response.get("code", 500)
    if not isinstance(code, int):
        code = 500
    return code

def submission_responses_layout(responses):
    cfg = config.config().config
    form = pm.setParent(q=True)
    pm.formLayout(form, edit=True, width=300)
    text = pm.text(label="Links to {}".format(cfg["auth_url"]))
    b1 = pm.button(label="Close", command=pm.Callback(_okay))
    scroll = pm.scrollLayout(bv=True)

    pm.setParent("..")
    layout_form(form, text, scroll, b1)
    pm.setParent(scroll)
    pm.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10)
    for success_uri in [
        response["response"]["uri"].replace("jobs", "job")
        for response in responses
        if _get_numeric_code(response) <= 201
    ]:
        job_url = parse.urljoin(cfg["auth_url"], success_uri)
        label = '<a href="{}"><font  color=#ec6a17 size=4>{}</font></a>'.format(
            job_url, job_url
        )
        pm.text(hl=True, label=label)

    failed_submissions = [response for response in responses if _get_numeric_code(response) > 201]
    num_failed = len(failed_submissions)
    if num_failed:
        pm.separator(style="single")
        pm.text(hl=True, label="{:d} failed submissions".format(num_failed))
        pm.separator(style="single")
        for failed_submission in failed_submissions:
            try:
                text = failed_submission["response"]
                pm.text(label=text, align="left", wordWrap=False)
            except BaseException as ex:
                pm.displayWarning(traceback.format_exc())


    pm.setParent(form)


def about_layout():
    form = pm.setParent(q=True)
    pm.formLayout(form, edit=True, width=300)
    heading = pm.text(label="Release Info and License")
    b1 = pm.button(label="Close", command=pm.Callback(_dismiss))
    frame = pm.frameLayout(
        bv=True, lv=False, cll=False, cl=False, width=700, height=500
    )
    pm.setParent("..")
    layout_form(form, heading, frame, b1)
    pm.setParent(frame)

    pm.scrollField(editable=False, wordWrap=True, text=about_conductor())

    pm.setParent(form)


def show_submission_responses(responses):
    return pm.layoutDialog(
        ui=pm.Callback(submission_responses_layout, responses), title="Render Response"
    )


def show_about():
    return pm.layoutDialog(ui=pm.Callback(about_layout), title="About Conductor Maya")
