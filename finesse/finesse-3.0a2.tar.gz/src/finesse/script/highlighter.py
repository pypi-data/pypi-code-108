"""KatScript lexer for syntax highlighting with Pygments."""


from pygments.lexer import Lexer, RegexLexer, using, bygroups
import pygments
import pygments.token as token
import re


class KatScriptPygmentsLexer(Lexer):
    name = "KatScript"
    aliases = ["katscript", "kat"]
    filenames = ["*.kat"]

    # Default map of KatToken types to pygments.token types.
    token_map = {
        # POWER and FLOORDIVIDE aren't needed since Pygments instead assumes these to be
        # two TIMES and DIVIDE tokens respectively.
        "COMMENT": token.Comment,
        "BOOLEAN": token.Keyword.Reserved,
        "NONE": token.Text,
        "REFERENCE": token.Name.Variable,
        "NUMBER": token.Number,
        "DIVIDE": token.Operator,
        "EQUALS": token.Operator,
        "MINUS": token.Operator,
        "PLUS": token.Operator,
        "TIMES": token.Operator,
        "COMMA": token.Punctuation,
        "LPAREN": token.Punctuation,
        "RPAREN": token.Punctuation,
        "LBRACKET": token.Punctuation,
        "RBRACKET": token.Punctuation,
        "STRING": token.String,
        "NAME": token.Text,
        "NEWLINE": token.Text,
        "WHITESPACE": token.Text,
    }

    def get_tokens_unprocessed(self, text):
        from finesse.script.parser import KatParser
        import finesse.script.containers as containers

        parser = KatParser()
        script = parser.parse(text)

        # Many tokens are typed as "NAME", with no other information available in
        # `script.sorted_tokens`. We therefore first do a pass through
        # `script.arguments` (where this information is available), and tag those that
        # have some special meaning.
        for arg in script.arguments:
            if type(arg) == containers.KatFunction:
                arg.directive._syntax_highlight_type = token.Name.Function.Magic
            elif type(arg) == containers.KatElement:
                arg.directive._syntax_highlight_type = token.Keyword.Type
                arg.name._syntax_highlight_type = token.Text

        for tok in script.sorted_tokens:
            if type(tok) == containers.KatMetaToken:
                continue
            elif hasattr(tok, "_syntax_highlight_type"):
                # If we've already tagged this token, just use the tagged type.
                yield tok.start_index, tok._syntax_highlight_type, tok.raw_value
            elif tok.type == "NAME" and "." in tok.raw_value:
                # Assume any "foo.bar" style tokens are variables.
                split = tok.raw_value.split(".")
                yield tok.start_index, token.Text, split[0]

                pos = tok.start_index + len(split[0])
                for s in split[1:]:
                    yield pos, token.Punctuation, "."
                    pos += 1
                    yield pos, token.Text, s
                    pos += len(s)
            elif tok.type == "REFERENCE":
                # Don't highlight the initial "&" in a reference, as it's really an
                # operator.
                yield tok.start_index, token.Operator, tok.raw_value[0]
                yield tok.start_index + 1, self.token_map[tok.type], tok.raw_value[1:]
            else:
                yield tok.start_index, self.token_map[tok.type], tok.raw_value


class KatScriptSubstringPygmentsLexer(RegexLexer):
    name = "KatScriptInPython"
    aliases = ["katscriptinpython"]

    flags = re.DOTALL

    tokens = {
        "root": [
            (
                r'(.+?""")([\s\n]*#kat)',
                bygroups(using(pygments.lexers.python.PythonLexer), None),
                "katscript",
            ),
            (".+", using(pygments.lexers.python.PythonLexer)),
        ],
        "katscript": [
            (
                '(.*?)(""")',
                bygroups(
                    using(KatScriptPygmentsLexer),
                    using(pygments.lexers.python.PythonLexer),
                ),
                "#pop",
            ),
        ],
    }
