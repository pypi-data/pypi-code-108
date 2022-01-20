import os

import markdown

from weasyprint import HTML

from mkdpdf import configuration
from mkdpdf.pdf.publisher import PDFPublisher

class PDF(PDFPublisher):
    """
    PDF is a Portable Document Format render object.
    """

    def __init__(self, directory_path_templates: str):
        """
        Args:
            directory_path_templates (string): path of templates directory
        """

        # update self
        self.directory_path_templates = directory_path_templates
        self.stylesheets = [
            os.path.join(configuration.DIRECTORY_PATH_PACKAGE, "document", "templates", "pdf", "style", "reset.css"),
            os.path.join(configuration.DIRECTORY_PATH_PACKAGE, "document", "templates", "pdf", "style", "pdf.css")
        ]
        self.template = directory_path_templates.split("/")[-3]

    def configure_overlay(self, type: str, content: str) -> tuple:
        """
        Configure overlay element (most commonly a header or footer).

        Args:
            content (string): HTML partial
            type (enum): header || footer

        Returns:
            A tuple where 0 == element, 1 == height for the element.
        """

        # add core partial style
        styles = self.stylesheets + [os.path.join(configuration.DIRECTORY_PATH_PACKAGE, "document", "templates", "pdf", "style", "%s.css" % type)]

        # update stylesheets
        styles += [os.path.join(self.directory_path_templates, "style", "%s.css" % type)]

        # calculate space requirement
        element, height = self._compute_overlay_element(type, content, styles)

        return (element, height)

    def construct(self, header: str, main: str, footer: str) -> str:
        """
        Construct complete document.

        Args:
            footer (string): HTML partial
            header (string): HTML partial
            main (string): HTML partial

        Returns:
            A Weasyprint object representing the main content of document.
        """

        footer_body = None
        footer_height = 0
        header_body = None
        header_height = 0

        # account for overlays
        if header:

            # wrap in required tag if not already
            if (isinstance(header, str) and not header.startswith("<header>")) or (isinstance(header, str) and not header.endswith("</header>")):
                header = "<header>%s</header>" % header

            # calculate space
            header_body, header_height = self.configure_overlay("header", header)

        if footer:

            # wrap in required tag if not already
            if (isinstance(footer, str) and not footer.startswith("<footer>")) or (isinstance(footer, str) and not footer.endswith("</footer>")):
                footer = "<footer>%s</footer>" % footer

            # calculate space
            footer_body, footer_height = self.configure_overlay("footer", footer)

        # if not core document class
        if self.template != "document":

            # add core partial style
            self.stylesheets += [os.path.join(configuration.DIRECTORY_PATH_PACKAGE, "document", "templates", "pdf", "style", "document.css")]

        # update stylesheets
        self.stylesheets += [os.path.join(self.directory_path_templates, "style", "document.css")]

        if main:

            # wrap in required tag if not already
            if (isinstance(main, str) and not main.startswith("<main>")) or (isinstance(main, str) and not main.endswith("</main>")):
                main = "<main>%s</main>" % main

        else:

            # set empty content
            main = "<main></main>"

        # generate main body
        main_body = HTML(
            string=main,
            base_url="/notebooks"
        ).render(
            stylesheets=self.stylesheets
        )

        # check for overlays
        if header or footer:

            # generate with overlays
            self._apply_overlay_on_main(main_body, header_body, footer_body)

        return main_body

    def render(self, content, file_path: str):
        """
        Render to filesystem as PDF file.

        Args:
            content ():
            file_path (string): ouput file path
        """

        # write to filesystem
        content.write_pdf(target=file_path)

    def table(self, content: str) -> str:
        """
        Generate HTML table partial from markdown string.

        Args:
            content (string): markdown string table representation

        Returns:
            A string representing an HTML partial to render a table.
        """

        return markdown.markdown(content, extensions=["markdown.extensions.tables"])
