"""Use Jinja2 templates with Extender.

This extension to Extender allows you to use Jinja2 in
email templates for both Extender and EFT emails.
"""
from datetime import datetime
from jinja2 import BaseLoader, TemplateNotFound, Environment
from extools.view import exview
from extools.view.errors import ExViewRecordDoesNotExist, ExViewError
from extools.message import logger_for_module

def get_template_environment(rotoid="VI0008"):
    template_loader = ExtenderTemplateLoader(rotoid)
    template_env = Environment(loader=template_loader)
    template_env.filters['strftime'] = strftime
    template_env.filters['strfdate'] = strfdate

    return template_env

class ExtenderTemplateLoader(BaseLoader):

    def __init__(self, template_rotoid="VI0008"):
        self.template_rotoid = template_rotoid
        self.log = logger_for_module("extools")

    def get_source(self, environment, template):
        section = 'body'
        if ':' in template:
            template, section = template.split(':')
            section = section.lower()

        content = ""
        try:
            self.log.debug("getting source for {}.{} [{}.MSGID={}]".format(
                template, self.template_rotoid, section, template))
            with exview(self.template_rotoid, seek_to={"MSGID": template}) as message_template:
                if section == 'body':
                    content = message_template.body
                    for i in range(2, 11):
                        content += message_template.get("BODY{}".format(i))
                else:
                    content = message_template.subject
        except ExViewError as e:
            self.log.error("Exception loading {}: {}".format(
                    template, e), exc_info=True)
            raise TemplateNotFound(template)

        return content, None, lambda: False

def strfdate(input, format="%Y-%m-%d"):
    """Render Extender Float Times."""
    if not input:
        return ""
    if isinstance(input, datetime):
        dt = input
    else:
        if isinstance(input, str):
            dt = input.split(".")[0]
        else:
            dt = str(int(input))
        dt = datetime.strptime(dt, "%Y%m%d")
    return dt.strftime(format)

def strftime(input, format="%H%M%S"):
    """Render Extender Float Dates."""
    if not input:
        return ""
    if isinstance(input, datetime):
        dt = input
    else:
        if isinstance(input, str):
            dt = input.split(".")[0]
        else:
            dt = str(int(input))
        dt = dt.zfill(8)[:6]
        dt = datetime.strptime(dt, "%H%M%S")
    return dt.strftime(format)
