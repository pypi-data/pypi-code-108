import os

import antlr4

from antlr4.error.ErrorListener import ErrorListener

from .jsonparse.JSONLexer import JSONLexer
from .jsonparse.JSONParser import JSONParser


class SyntaxErrorException(Exception):
    def __init__(self, content):
        Exception.__init__(self, content)


class CustomErrorListener(ErrorListener):
    def syntaxError(self, r, s, line, col, msg, e):
        raise SyntaxErrorException("Line:%d, Column: %d: %s" % (line, col, msg))


def format_file(filecontent, file_path=None, json_extension_only=True):
    if not filecontent:
        return filecontent

    if isinstance(filecontent, str):
        filecontent = filecontent.encode("utf-8")

    if json_extension_only and file_path and not file_path.endswith(".json"):
        return filecontent.decode("utf-8")

    if file_path and file_path.endswith("graph.json"):
        return filecontent.decode("utf-8")

    try:
        return DKJSONParser.to_string(DKJSONParser.parse_string(filecontent), indent=4, newlines=True)
    except Exception as e:
        if filecontent is None:
            content = "(null)"
        else:
            content = str(filecontent)
            if len(content) > 30:
                content = content[:30]
        print('DKJSONParser.format_file error {}; content "{}"'.format(e, content))

    return filecontent


def _process_line(line, indent, is_last_line, ends_with_newline):

    index_nonwhitespace = len(line) - len(line.lstrip())
    new_line = ""
    for i in range(index_nonwhitespace):
        if line[i] == "\t":
            new_line += " " * indent
        else:
            new_line += line[i]

    # add the remainder of the string and "os.linesep" (if necessary):
    new_line += line[index_nonwhitespace:]
    # if this is not the last line, or (is_last_line and ends_with_newline), add "os.linesep":
    if not is_last_line or is_last_line and ends_with_newline:
        new_line += os.linesep

    return new_line


# In conformity with PEP 8 standard, converts all tabs at the beginning of lines
# (unless there are other spaces) into "indent" (default 4) spaces
def format_python_file(filecontent, file_path=None, indent=4):

    if not filecontent:
        return filecontent

    if file_path and not file_path.endswith(".py"):
        return filecontent

    str_filecontent = str(filecontent)
    ends_with_newline = True if str_filecontent.endswith(os.linesep) else False
    lines = str_filecontent.splitlines()
    length = len(lines)
    formatted_file_str = ""
    for i in range(length):
        formatted_line = _process_line(lines[i], indent, i == length - 1, ends_with_newline)
        formatted_file_str += formatted_line

    return formatted_file_str


class DKJSONParser(object):
    @staticmethod
    def parse_string(jsondata):
        if (jsondata is None) or isinstance(jsondata, str):
            result = antlr4.InputStream(jsondata)
        else:
            result = antlr4.InputStream(jsondata.decode("utf-8"))
        return DKJSONParser._parse(result)

    @staticmethod
    def parse_file(fileobj, encoding="ascii"):
        return DKJSONParser._parse(antlr4.FileStream(fileobj, encoding))

    @staticmethod
    def _parse(datastream):
        listener = CustomErrorListener()
        lexer = JSONLexer(datastream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(listener)

        stream = antlr4.CommonTokenStream(lexer)
        parser = JSONParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(listener)
        return parser.json().val

    @staticmethod
    def to_string(obj, indent=0, newlines=False):
        return DKJSONParser._write_val(obj, indent, 0, newlines)

    @staticmethod
    def _write_val(val, indent, level, newlines):
        if val is None:
            return "null"
        elif val is True:
            return "true"
        elif val is False:
            return "false"
        elif isinstance(val, str):
            return '"%s"' % val
        elif isinstance(val, int):
            return str(val)
        elif isinstance(val, float):
            return str(val)
        elif isinstance(val, dict):
            return DKJSONParser._write_dict(val, indent, level, newlines)
        elif isinstance(val, list):
            return DKJSONParser._write_array(val, indent, level, newlines)
        else:
            return ""

    @staticmethod
    def _indent(indent, level):
        return " " * (indent * level)

    @staticmethod
    def _write_pair(k, v, indent, level, newlines):
        return '%s"%s": %s' % (
            DKJSONParser._indent(indent, level),
            k,
            DKJSONParser._write_val(v, indent, level, newlines),
        )

    @staticmethod
    def _write_dict(obj, indent, level, newlines):

        padding = DKJSONParser._indent(indent, level)

        def _format_pair(p):
            k, v = p
            return DKJSONParser._write_pair(k, v, indent, level + 1, newlines)

        nl = "\n" if newlines else ""

        return "{" + nl + (", %s" % nl).join(map(_format_pair, obj.items())) + nl + padding + "}" + nl

    @staticmethod
    def _write_array(arr, indent, level, newlines):

        padding = DKJSONParser._indent(indent, level + 1)

        def write_val(v):
            return padding + DKJSONParser._write_val(v, indent, level + 1, newlines)

        nl = "\n" if newlines else ""

        return "[" + nl + (", %s" % nl).join(map(write_val, arr)) + DKJSONParser._indent(indent, level) + "]"
