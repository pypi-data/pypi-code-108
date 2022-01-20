from weasyprint import HTML, CSS

from mkdpdf import configuration

class PDFPublisher:
    """
    PDFPublisher is a weasyprint publisher.

    Reference: https://weasyprint.readthedocs.io/en/latest/tips-tricks.html#include-header-and-footer-of-arbitrary-complexity-in-a-pdf
    """

    # defaults
    base_url = None
    extra_vertical_margin = configuration.DOCUMENT_EXTRA_VERTICAL_MARGIN
    side_margin = configuration.DOCUMENT_SIDE_MARGIN

    def __init__(self, date_publish: str = configuration.DATE_PUBLISH):
        """
        Args:
            date_publish (string): iso 8601 date value
        """

        # initialize inheritance
        super(PDFPublisher, self).__init__(
            date_publish=date_publish
        )

    def _apply_overlay_on_main(self, main_doc, header_body=None, footer_body=None):
        """
        Insert the header and the footer in the main document.

        Args:
            main_doc (Document): top-level representation for a PDF page in weasyprint
            header_body (BlockBox): representation for an html element in weasyprint
            footer_body (BlockBox): representation for an html element in weasyprint
        """

        for page in main_doc.pages:
            page_body = self._get_element(page._page_box.all_children())

            if header_body:
                page_body.children += header_body.all_children()
            if footer_body:
                page_body.children += footer_body.all_children()

    def _compute_overlay_element(self, element: str, html_partial: str, stylesheets: list):
        """
        Args:
            element (enum): header | footer
            html_partial (string): html content
            stylesheets (list): strings representing css file paths

        Returns:
            A tuple of (element_body, element_height) which are 0 == (BlockBox) weasyprint pre-rendered representation of an html element, 1 == (float) height of this element, which will be then translated in a html height.
        """

        html = HTML(base_url=self.base_url, string=html_partial)

        element_doc = html.render(stylesheets=stylesheets)
        element_page = element_doc.pages[0]
        element_body = self._get_element(element_page._page_box.all_children())
        element_body = element_body.copy_with_children(element_body.all_children())
        element_html = self._get_element(element_page._page_box.all_children())

        if element == "header":
            element_height = element_html.height
        if element == "footer":
            element_height = element_page.height - element_html.position_y

        return element_body, element_height

    def _get_element(self, boxes):
        """
        Given a set of boxes representing the elements of a PDF page in a DOM-like way, find the
        box which is named `element`.

        Look at the notes of the class for more details on Weasyprint insides.

        Args:
            boxes (list): list of elements

        Returns:
            A BlockBox representing the html element named `element`.
        """

        for box in boxes:
            if box.element_tag == "body":
                return box
            return self._get_element(box.all_children())
