from contextlib import contextmanager
from gettext import gettext as _

import click


class SotoonHelpFormatter(click.HelpFormatter):
    def __init__(self, width=None, max_width=None):
        super().__init__(width=width, max_width=max_width)

    @contextmanager
    def write_bold_heading(self, text):
        self.write_paragraph()
        self.write_heading(click.style(text, bold=True))
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    def write_usage(self, prog, args="", prefix="Usage"):
        with self.write_bold_heading(_(prefix)):
            self.write(
                click.formatting.wrap_text(  # TODO: rewrite
                    f"{click.style(prog, bold=True)} {args}",
                    150,  # TODO: why self.width is not enough?
                    initial_indent=self.current_indent * " ",
                    subsequent_indent=self.current_indent * " " * 3,
                    preserve_paragraphs=True,
                )
            )
        self.write("\n")
        # with self.write_bold_heading(_(prefix)):
        #     self.write_text(f"{click.style(prog, bold=True)} {args}")
