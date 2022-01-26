#!/usr/bin/env python
"""
    args.py                          Nat Goodspeed
    Copyright (C) 2017-2021          Nat Goodspeed

NRG 2017-02-01
"""

from argparse import ArgumentParser, HelpFormatter
import re

class ParagraphHelpFormatter(HelpFormatter):
    """
    The only thing we want to change about HelpFormatter is that we don't
    want ALL our text reflowed: we want to recognize '\n\n' as a paragraph
    separator, flow each paragraph separately and rejoin them at the end.

    The tricky thing is that we also want to be able to introduce explicit
    line breaks. Append '\n' (literally those two characters) to the end
    of a line to force a line break there.
    """
    # either two newlines in sequence or literally (backslash, n, newline)
    paragraph_break = re.compile(r'(\n\n|\\n\n)')
    def _fill_text(self, text, *args, **kwds):
        # First, split text into pieces on paragraph_breaks. Because we
        # used capture parentheses in paragraph_break, the resulting list
        # contains the delimiters as well as the pieces of text they
        # delimit.
        # Walk that list, checking each p (again) to see if it matches
        # paragraph_break. If it does -- and if it's the (backslash, n,
        # newline) form of delimiter -- remove (backslash, n), leaving
        # only the newline. If it's just (newline, newline), leave both.
        # But if p isn't a paragraph_break, it's text, so format it by
        # calling our base-class _fill_text() method.
        # Either way, rejoin ALL the individual bits at the end.
        return ''.join(
            ((p[2:] if p.startswith(r'\n') else p)
             if self.paragraph_break.match(p)
             else super(ParagraphHelpFormatter, self)._fill_text(p, *args, **kwds))
            for p in self.paragraph_break.split(text))

class ParagraphArgumentParser(ArgumentParser):
    """
    The name of this class means that it formats verbose --help text into
    distinct paragraphs. It doesn't mean it parses paragraphs.

    Use this subclass when you have so much to say in --help (in description=,
    epilog= et al.) that you want to break it into paragraphs, with each
    paragraph formatted individually rather than all of them mushed together
    into a single paragraph.

    The ParagraphHelpFormatter above implements this behavior. It extends
    argparse.HelpFormatter by recognizing two kinds of explicit breaks within
    description= or epilog= help text:

    - Leave a completely empty line (that is, '\n\n') in your description text
      to separate paragraphs normally.

    - Additionally, any backslash-n-newline sequence ('\\n\n', the two
      characters \n at the end of a text line) forces a formatting break,
      retaining the newline while discarding the backslash-n.

    Otherwise this class behaves identically to argparse.ArgumentParser.
    """
    def __init__(self, *args, **kwds):
        # It's unclear to me why anyone would choose to use
        # ParagraphArgumentParser and *also* override formatter_class -- but we
        # support it anyway, at least as an explicit keyword override. We
        # should neither know nor have to care about the order in which our
        # base-class __init__() declares its parameters.
        help_formatter = kwds.pop("formatter_class", ParagraphHelpFormatter)

        # Pass that help_formatter to base-class __init__() along with
        # everything else.
        super(ParagraphArgumentParser, self).__init__(
            formatter_class=help_formatter, *args, **kwds)
