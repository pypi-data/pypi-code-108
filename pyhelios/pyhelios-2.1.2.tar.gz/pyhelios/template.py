import os
import jinja2


def get_jinja_latex_template(template):
    options = dict()
    options["block_start_string"] = "\BLOCK{"
    options["block_end_string"] = "}"
    options["variable_start_string"] = "\VAR{"
    options["variable_end_string"] = "}"
    options["comment_start_string"] = "\#{"
    options["comment_end_string"] = "}"
    options["line_statement_prefix"] = "%%"
    options["line_comment_prefix"] = "%#"
    options["trim_blocks"] = True
    options["autoescape"] = False
    if os.path.isfile(template):
        dirname = os.path.dirname(template)
        basename = os.path.basename(template)
        options["loader"] = jinja2.FileSystemLoader(dirname)
        env = jinja2.Environment(**options)
        return env.get_template(basename)
    else:
        env = jinja2.Environment(**options)
        return env.from_string(template)


def render(template, output, data):
    options = {}
    options["trim_blocks"] = True
    options["autoescape"] = False
    dirname = os.path.dirname(template)
    basename = os.path.basename(template)
    options["loader"] = jinja2.FileSystemLoader(dirname)
    tmp = jinja2.Environment(**options).get_template(basename)
    with open(output, "w") as fid:
        fid.write(tmp.render(data))
